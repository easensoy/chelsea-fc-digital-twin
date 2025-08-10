from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import logging
import json

from .models import Formation, Player, Match, Opponent, PlayerStats, TeamStats, MatchLineup, Analytics
from .formation_engine import FormationEngine
from .tactical_analyzer import TacticalAnalyzer
from .performance_tracker import PerformanceTracker

logger = logging.getLogger('core.performance')

class RecommendationSystem:
    
    def __init__(self):
        self.formation_engine = FormationEngine()
        self.tactical_analyzer = TacticalAnalyzer()
        self.performance_tracker = PerformanceTracker()
        self.logger = logging.getLogger('core.performance')
        self.confidence_threshold = 0.7
        
    def get_formation_recommendations(self, opponent_id=None, match_type='LEAGUE', available_players=None):
        recommendations = {
            'primary_recommendation': None,
            'alternative_recommendations': [],
            'tactical_considerations': [],
            'player_recommendations': [],
            'confidence_score': 0,
            'analysis_summary': '',
            'risk_assessment': {}
        }
        
        if available_players is None:
            available_players = Player.objects.filter(is_active=True, is_injured=False)
        
        opponent = None
        if opponent_id:
            try:
                opponent = Opponent.objects.get(id=opponent_id)
            except Opponent.DoesNotExist:
                self.logger.warning(f"Opponent with ID {opponent_id} not found")
        
        formation_scores = self._evaluate_all_formations(opponent, match_type, available_players)
        
        if not formation_scores:
            return self._default_recommendations()
        
        sorted_formations = sorted(formation_scores.items(), key=lambda x: x[1]['total_score'], reverse=True)
        
        primary_formation, primary_data = sorted_formations[0]
        recommendations['primary_recommendation'] = self._format_recommendation(primary_formation, primary_data, 'Primary')
        
        for formation, data in sorted_formations[1:4]:
            alt_rec = self._format_recommendation(formation, data, 'Alternative')
            recommendations['alternative_recommendations'].append(alt_rec)
        
        recommendations['tactical_considerations'] = self._generate_tactical_considerations(
            opponent, match_type, primary_formation, primary_data
        )
        
        recommendations['player_recommendations'] = self._generate_player_recommendations(
            primary_formation, available_players, opponent
        )
        
        recommendations['confidence_score'] = self._calculate_overall_confidence(primary_data)
        recommendations['analysis_summary'] = self._generate_analysis_summary(
            primary_formation, opponent, primary_data
        )
        recommendations['risk_assessment'] = self._assess_formation_risks(
            primary_formation, opponent, primary_data
        )
        
        self._save_recommendation_analytics(recommendations, opponent, match_type)
        
        return recommendations
    
    def _evaluate_all_formations(self, opponent, match_type, available_players):
        formations = Formation.objects.filter(is_active=True)
        formation_scores = {}
        
        for formation in formations:
            score_data = self._score_formation(formation, opponent, match_type, available_players)
            if score_data['total_score'] > 0:
                formation_scores[formation] = score_data
        
        return formation_scores
    
    def _score_formation(self, formation, opponent, match_type, available_players):
        score_components = {
            'historical_performance': self._score_historical_performance(formation, match_type),
            'opponent_effectiveness': self._score_against_opponent(formation, opponent),
            'player_suitability': self._score_player_suitability(formation, available_players),
            'tactical_compatibility': self._score_tactical_compatibility(formation, opponent),
            'recent_form': self._score_recent_form(formation),
            'match_context': self._score_match_context(formation, match_type, opponent)
        }
        
        weights = {
            'historical_performance': 0.25,
            'opponent_effectiveness': 0.20,
            'player_suitability': 0.20,
            'tactical_compatibility': 0.15,
            'recent_form': 0.15,
            'match_context': 0.05
        }
        
        total_score = sum(
            score_components[component] * weights[component]
            for component in score_components
        )
        
        return {
            'total_score': round(total_score, 2),
            'component_scores': score_components,
            'weights_used': weights,
            'confidence': self._calculate_score_confidence(score_components)
        }
    
    def _score_historical_performance(self, formation, match_type):
        effectiveness_data = self.formation_engine.calculate_formation_effectiveness(formation)
        
        if effectiveness_data['matches_analyzed'] < 3:
            return 50
        
        base_score = effectiveness_data['effectiveness_score']
        
        if match_type in ['UCL', 'UEL', 'FA', 'CARABAO']:
            cup_matches = self._get_cup_performance(formation, match_type)
            if cup_matches:
                cup_modifier = self._calculate_cup_performance_modifier(cup_matches)
                base_score = (base_score * 0.7) + (cup_modifier * 0.3)
        
        return min(100, max(0, base_score))
    
    def _score_against_opponent(self, formation, opponent):
        if not opponent:
            return 60
        
        effectiveness_data = self.formation_engine.calculate_formation_effectiveness(formation)
        opponent_specific = effectiveness_data.get('opponent_specific')
        
        if opponent_specific and opponent_specific['matches_against'] > 0:
            opponent_score = opponent_specific['win_rate']
            goal_difference = opponent_specific['average_goals_scored'] - opponent_specific['average_goals_conceded']
            
            if goal_difference > 0:
                opponent_score += min(20, goal_difference * 10)
            else:
                opponent_score += max(-20, goal_difference * 10)
            
            return min(100, max(0, opponent_score))
        
        similar_opponents_score = self._score_against_similar_opponents(formation, opponent)
        return similar_opponents_score
    
    def _score_against_similar_opponents(self, formation, opponent):
        similar_style_matches = Match.objects.filter(
            opponent__playing_style=opponent.playing_style,
            status__in=['COMPLETED', 'FULL_TIME']
        ).exclude(opponent=opponent)[:10]
        
        if not similar_style_matches:
            return 60
        
        formation_matches = []
        for match in similar_style_matches:
            try:
                lineup = MatchLineup.objects.get(match=match, formation=formation, is_starting_eleven=True)
                formation_matches.append(match)
            except MatchLineup.DoesNotExist:
                continue
        
        if not formation_matches:
            return 60
        
        wins = sum(1 for match in formation_matches if match.result == 'WIN')
        win_rate = (wins / len(formation_matches)) * 100
        
        goals_scored = sum(match.chelsea_score for match in formation_matches)
        goals_conceded = sum(match.opponent_score for match in formation_matches)
        avg_goal_diff = (goals_scored - goals_conceded) / len(formation_matches)
        
        similarity_score = win_rate + (avg_goal_diff * 10)
        return min(100, max(0, similarity_score))
    
    def _score_player_suitability(self, formation, available_players):
        position_requirements = self._get_formation_position_requirements(formation.name)
        
        suitability_scores = []
        
        for position, required_count in position_requirements.items():
            suitable_players = available_players.filter(position=position)
            
            if suitable_players.count() >= required_count:
                avg_fitness = suitable_players.aggregate(avg=Avg('fitness_level'))['avg'] or 0
                position_score = min(100, avg_fitness * 1.2)
                
                top_players = suitable_players.order_by('-fitness_level')[:required_count]
                recent_performance = self._get_recent_player_performance(top_players)
                
                combined_score = (position_score * 0.6) + (recent_performance * 0.4)
                suitability_scores.append(combined_score)
            else:
                shortage_penalty = (required_count - suitable_players.count()) * 25
                suitability_scores.append(max(0, 50 - shortage_penalty))
        
        return sum(suitability_scores) / len(suitability_scores) if suitability_scores else 0
    
    def _score_tactical_compatibility(self, formation, opponent):
        if not opponent:
            return 70
        
        formation_style = self._determine_formation_style(formation.name)
        opponent_style = opponent.playing_style.lower() if opponent.playing_style else 'balanced'
        
        compatibility_matrix = {
            'attacking': {
                'defensive': 85,
                'balanced': 75,
                'attacking': 60,
                'counter-attacking': 70
            },
            'defensive': {
                'defensive': 50,
                'balanced': 70,
                'attacking': 90,
                'counter-attacking': 60
            },
            'balanced': {
                'defensive': 75,
                'balanced': 80,
                'attacking': 75,
                'counter-attacking': 75
            },
            'counter-attacking': {
                'defensive': 65,
                'balanced': 80,
                'attacking': 95,
                'counter-attacking': 70
            }
        }
        
        return compatibility_matrix.get(formation_style, {}).get(opponent_style, 70)
    
    def _score_recent_form(self, formation):
        recent_matches = self._get_formation_matches_recent(formation, days=21)
        
        if len(recent_matches) < 2:
            return 60
        
        wins = sum(1 for match in recent_matches if match.result == 'WIN')
        draws = sum(1 for match in recent_matches if match.result == 'DRAW')
        
        win_rate = (wins / len(recent_matches)) * 100
        draw_bonus = (draws / len(recent_matches)) * 20
        
        recent_goals = sum(match.chelsea_score for match in recent_matches)
        recent_conceded = sum(match.opponent_score for match in recent_matches)
        goal_diff_bonus = ((recent_goals - recent_conceded) / len(recent_matches)) * 15
        
        form_score = win_rate + draw_bonus + goal_diff_bonus
        return min(100, max(0, form_score))
    
    def _score_match_context(self, formation, match_type, opponent):
        base_score = 70
        
        context_modifiers = {
            'UCL': 10,
            'UEL': 5,
            'FA': 0,
            'CARABAO': -5,
            'LEAGUE': 0,
            'FRIENDLY': -10
        }
        
        base_score += context_modifiers.get(match_type, 0)
        
        if opponent and opponent.league.lower() == 'premier league':
            base_score += 5
        elif opponent and 'championship' in opponent.league.lower():
            base_score -= 5
        
        return min(100, max(0, base_score))
    
    def _get_formation_position_requirements(self, formation_name):
        requirements = {
            '4-4-2': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CM': 2, 'LM': 1, 'RM': 1, 'ST': 2},
            '4-3-3': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 1, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 1},
            '3-5-2': {'GK': 1, 'CB': 3, 'CDM': 1, 'CM': 2, 'LM': 1, 'RM': 1, 'ST': 2},
            '5-3-2': {'GK': 1, 'CB': 3, 'LB': 1, 'RB': 1, 'CDM': 1, 'CM': 2, 'ST': 2},
            '4-2-3-1': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 2, 'CAM': 1, 'LM': 1, 'RM': 1, 'ST': 1},
            '3-4-3': {'GK': 1, 'CB': 3, 'CDM': 1, 'CM': 2, 'CAM': 1, 'LW': 1, 'RW': 1, 'ST': 1}
        }
        
        return requirements.get(formation_name, {})
    
    def _get_recent_player_performance(self, players):
        if not players:
            return 50
        
        recent_stats = PlayerStats.objects.filter(
            player__in=players,
            match__scheduled_datetime__gte=timezone.now() - timedelta(days=30),
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if not recent_stats.exists():
            return 50
        
        avg_rating = recent_stats.aggregate(avg=Avg('rating'))['avg'] or 5.0
        return min(100, (float(avg_rating) - 5.0) * 25 + 50)
    
    def _determine_formation_style(self, formation_name):
        attacking_formations = ['4-3-3', '3-4-3', '4-2-3-1']
        defensive_formations = ['5-3-2', '5-4-1']
        counter_attacking_formations = ['3-5-2']
        
        if formation_name in attacking_formations:
            return 'attacking'
        elif formation_name in defensive_formations:
            return 'defensive'
        elif formation_name in counter_attacking_formations:
            return 'counter-attacking'
        else:
            return 'balanced'
    
    def _get_formation_matches_recent(self, formation, days=21):
        cutoff_date = timezone.now() - timedelta(days=days)
        
        lineups = MatchLineup.objects.filter(
            formation=formation,
            match__status__in=['COMPLETED', 'FULL_TIME'],
            match__scheduled_datetime__gte=cutoff_date,
            is_starting_eleven=True
        ).select_related('match')
        
        return [lineup.match for lineup in lineups]
    
    def _get_cup_performance(self, formation, match_type):
        cup_matches = Match.objects.filter(
            match_type=match_type,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        formation_cup_matches = []
        for match in cup_matches:
            try:
                lineup = MatchLineup.objects.get(match=match, formation=formation, is_starting_eleven=True)
                formation_cup_matches.append(match)
            except MatchLineup.DoesNotExist:
                continue
        
        return formation_cup_matches
    
    def _calculate_cup_performance_modifier(self, cup_matches):
        if not cup_matches:
            return 50
        
        wins = sum(1 for match in cup_matches if match.result == 'WIN')
        win_rate = (wins / len(cup_matches)) * 100
        
        return min(100, max(0, win_rate))
    
    def _calculate_score_confidence(self, score_components):
        data_availability = 0
        
        if score_components['historical_performance'] != 50:
            data_availability += 25
        if score_components['opponent_effectiveness'] != 60:
            data_availability += 20
        if score_components['player_suitability'] > 0:
            data_availability += 25
        if score_components['recent_form'] != 60:
            data_availability += 20
        if score_components['tactical_compatibility'] != 70:
            data_availability += 10
        
        return min(100, data_availability)
    
    def _format_recommendation(self, formation, data, recommendation_type):
        return {
            'formation_name': formation.name,
            'formation_id': str(formation.id),
            'recommendation_type': recommendation_type,
            'confidence_score': data['confidence'],
            'total_score': data['total_score'],
            'strengths': self._identify_formation_strengths(formation, data),
            'considerations': self._identify_formation_considerations(formation, data),
            'component_breakdown': data['component_scores']
        }
    
    def _identify_formation_strengths(self, formation, data):
        strengths = []
        
        if data['component_scores']['historical_performance'] >= 75:
            strengths.append("Strong historical performance record")
        
        if data['component_scores']['opponent_effectiveness'] >= 80:
            strengths.append("Excellent effectiveness against this type of opposition")
        
        if data['component_scores']['player_suitability'] >= 85:
            strengths.append("Optimal fit for available squad players")
        
        if data['component_scores']['recent_form'] >= 80:
            strengths.append("Formation showing excellent recent form")
        
        if data['component_scores']['tactical_compatibility'] >= 85:
            strengths.append("High tactical compatibility with opposition style")
        
        return strengths
    
    def _identify_formation_considerations(self, formation, data):
        considerations = []
        
        if data['component_scores']['historical_performance'] < 60:
            considerations.append("Limited historical success with this formation")
        
        if data['component_scores']['player_suitability'] < 70:
            considerations.append("Some player positions may need tactical adjustments")
        
        if data['component_scores']['recent_form'] < 50:
            considerations.append("Formation has struggled in recent matches")
        
        if data['component_scores']['opponent_effectiveness'] < 50:
            considerations.append("Poor historical record against similar opponents")
        
        return considerations
    
    def _generate_tactical_considerations(self, opponent, match_type, primary_formation, primary_data):
        considerations = []
        
        if opponent:
            if opponent.typical_formation in ['4-3-3', '3-4-3']:
                considerations.append("Opposition likely to press high - ensure midfield numerical advantage")
            
            if 'attacking' in opponent.playing_style.lower():
                considerations.append("Opposition favours attacking play - strengthen defensive transitions")
            
            if 'defensive' in opponent.playing_style.lower():
                considerations.append("Expect defensive setup - focus on patient build-up and width")
        
        if match_type in ['UCL', 'UEL']:
            considerations.append("European competition - consider squad rotation and tactical flexibility")
        
        if primary_data['component_scores']['player_suitability'] < 80:
            considerations.append("Monitor player fitness levels throughout the match")
        
        return considerations
    
    def _generate_player_recommendations(self, formation, available_players, opponent):
        position_requirements = self._get_formation_position_requirements(formation.name)
        player_recommendations = []
        
        for position, required_count in position_requirements.items():
            suitable_players = available_players.filter(position=position).order_by('-fitness_level', '-market_value')
            
            if suitable_players.count() >= required_count:
                top_players = suitable_players[:required_count]
                
                for player in top_players:
                    recent_performance = self.performance_tracker.get_player_performance(player, days=14)
                    
                    recommendation = {
                        'player_name': player.full_name,
                        'position': position,
                        'fitness_level': player.fitness_level,
                        'recent_rating': recent_performance.get('average_rating', 0),
                        'recommendation_strength': self._calculate_player_recommendation_strength(player, recent_performance, opponent),
                        'tactical_notes': self._generate_player_tactical_notes(player, position, opponent)
                    }
                    
                    player_recommendations.append(recommendation)
            else:
                player_recommendations.append({
                    'position': position,
                    'issue': f"Insufficient players available for {position}",
                    'available_count': suitable_players.count(),
                    'required_count': required_count
                })
        
        return player_recommendations
    
    def _calculate_player_recommendation_strength(self, player, recent_performance, opponent):
        base_strength = min(100, player.fitness_level * 0.8 + recent_performance.get('average_rating', 5) * 10)
        
        if not player.is_injured and player.fitness_level >= 90:
            base_strength += 10
        
        if recent_performance.get('average_rating', 0) >= 7.5:
            base_strength += 15
        
        return min(100, max(0, base_strength))
    
    def _generate_player_tactical_notes(self, player, position, opponent):
        notes = []
        
        if player.fitness_level < 85:
            notes.append("Monitor stamina levels during match")
        
        if position in ['LW', 'RW', 'ST'] and opponent:
            if 'defensive' in opponent.playing_style.lower():
                notes.append("Focus on movement in tight spaces")
        
        if position in ['CB', 'CDM'] and opponent:
            if 'attacking' in opponent.playing_style.lower():
                notes.append("Prioritise defensive positioning and awareness")
        
        return notes
    
    def _calculate_overall_confidence(self, primary_data):
        component_confidence = primary_data['confidence']
        score_confidence = min(100, primary_data['total_score'])
        
        overall_confidence = (component_confidence * 0.6) + (score_confidence * 0.4)
        return round(overall_confidence, 2)
    
    def _generate_analysis_summary(self, formation, opponent, data):
        formation_name = formation.name
        total_score = data['total_score']
        
        summary = f"Formation {formation_name} recommended with {total_score:.1f}/100 overall score. "
        
        if opponent:
            summary += f"Analysis includes specific considerations for facing {opponent.name}. "
        
        if data['confidence'] >= 80:
            summary += "High confidence recommendation based on comprehensive data analysis."
        elif data['confidence'] >= 60:
            summary += "Moderate confidence recommendation with sufficient historical data."
        else:
            summary += "Lower confidence due to limited historical data - monitor performance closely."
        
        return summary
    
    def _assess_formation_risks(self, formation, opponent, data):
        risks = {
            'injury_risk': self._assess_injury_risk(formation),
            'tactical_risk': self._assess_tactical_risk(formation, opponent, data),
            'performance_risk': self._assess_performance_risk(data),
            'squad_depth_risk': self._assess_squad_depth_risk(formation)
        }
        
        overall_risk = sum(risks.values()) / len(risks)
        
        risks['overall_risk_level'] = (
            'High' if overall_risk >= 70 else
            'Medium' if overall_risk >= 40 else
            'Low'
        )
        
        return risks
    
    def _assess_injury_risk(self, formation):
        position_requirements = self._get_formation_position_requirements(formation.name)
        risk_score = 0
        
        for position, required_count in position_requirements.items():
            available_players = Player.objects.filter(
                position=position,
                is_active=True,
                is_injured=False
            )
            
            if available_players.count() <= required_count:
                risk_score += 25
            elif available_players.count() <= required_count + 1:
                risk_score += 10
        
        return min(100, risk_score)
    
    def _assess_tactical_risk(self, formation, opponent, data):
        risk_score = 0
        
        if data['component_scores']['opponent_effectiveness'] < 50:
            risk_score += 30
        
        if data['component_scores']['tactical_compatibility'] < 60:
            risk_score += 25
        
        if data['component_scores']['recent_form'] < 50:
            risk_score += 20
        
        return min(100, risk_score)
    
    def _assess_performance_risk(self, data):
        if data['total_score'] >= 80:
            return 10
        elif data['total_score'] >= 70:
            return 25
        elif data['total_score'] >= 60:
            return 50
        else:
            return 75
    
    def _assess_squad_depth_risk(self, formation):
        position_requirements = self._get_formation_position_requirements(formation.name)
        depth_scores = []
        
        for position, required_count in position_requirements.items():
            available_players = Player.objects.filter(
                position=position,
                is_active=True,
                is_injured=False,
                fitness_level__gte=80
            )
            
            depth_ratio = available_players.count() / max(required_count, 1)
            if depth_ratio >= 2:
                depth_scores.append(10)
            elif depth_ratio >= 1.5:
                depth_scores.append(25)
            elif depth_ratio >= 1:
                depth_scores.append(50)
            else:
                depth_scores.append(80)
        
        return sum(depth_scores) / len(depth_scores) if depth_scores else 50
    
    def _save_recommendation_analytics(self, recommendations, opponent, match_type):
        try:
            analytics_data = Analytics.objects.create(
                analysis_type='FORMATION_EFFECTIVENESS',
                title=f"Formation Recommendation - {match_type}",
                description=f"AI-generated formation recommendation for {match_type} match",
                data_points={
                    'match_type': match_type,
                    'opponent_id': str(opponent.id) if opponent else None,
                    'primary_formation': recommendations['primary_recommendation']['formation_name'] if recommendations['primary_recommendation'] else None,
                    'confidence_score': recommendations['confidence_score'],
                    'timestamp': timezone.now().isoformat()
                },
                insights=recommendations['tactical_considerations'],
                recommendations=[rec['formation_name'] for rec in recommendations['alternative_recommendations']],
                confidence_score=Decimal(str(recommendations['confidence_score'])),
                related_opponent=opponent
            )
            
            self.logger.info(f"Recommendation analytics saved: {analytics_data.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save recommendation analytics: {str(e)}")
    
    def _default_recommendations(self):
        return {
            'primary_recommendation': {
                'formation_name': '4-3-3',
                'formation_id': None,
                'recommendation_type': 'Default',
                'confidence_score': 50,
                'total_score': 50,
                'strengths': ['Balanced formation suitable for most situations'],
                'considerations': ['Limited specific analysis available'],
                'component_breakdown': {}
            },
            'alternative_recommendations': [
                {
                    'formation_name': '4-4-2',
                    'formation_id': None,
                    'recommendation_type': 'Alternative',
                    'confidence_score': 45,
                    'total_score': 45,
                    'strengths': ['Traditional formation with good balance'],
                    'considerations': ['May lack midfield control in some matches'],
                    'component_breakdown': {}
                }
            ],
            'tactical_considerations': ['Insufficient data for detailed tactical analysis'],
            'player_recommendations': [],
            'confidence_score': 30,
            'analysis_summary': 'Default recommendations provided due to insufficient data',
            'risk_assessment': {
                'overall_risk_level': 'Medium'
            }
        }