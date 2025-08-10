from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import logging
import random

from .models import Player, PlayerStats, Match, Formation, MatchLineup, TeamStats, Opponent
from .exceptions import InsufficientDataError, ValidationError

logger = logging.getLogger('core.performance')

class PredictionModels:
    
    def __init__(self):
        self.logger = logging.getLogger('core.performance')
        self.prediction_weights = {
            'recent_form': 0.4,
            'historical_record': 0.3,
            'player_fitness': 0.15,
            'tactical_suitability': 0.15
        }
        self.confidence_threshold = 0.6
    
    def predict_match_outcome(self, opponent, formation=None, days_analysis=90):
        if not isinstance(opponent, Opponent):
            raise ValidationError("Invalid opponent object provided")
        
        cutoff_date = timezone.now() - timedelta(days=days_analysis)
        
        historical_matches = Match.objects.filter(
            opponent=opponent,
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if historical_matches.count() < 2:
            return self._generate_limited_prediction(opponent, formation)
        
        prediction = {
            'opponent': opponent.name,
            'analysis_period': days_analysis,
            'prediction_confidence': 0,
            'predicted_outcome': self._calculate_outcome_probabilities(historical_matches, formation),
            'predicted_scoreline': self._predict_scoreline(historical_matches, formation),
            'key_factors': self._identify_key_prediction_factors(historical_matches, formation),
            'risk_assessment': self._assess_match_risks(historical_matches, opponent),
            'tactical_recommendations': self._generate_tactical_predictions(historical_matches, opponent, formation),
            'player_impact_predictions': self._predict_player_impacts(historical_matches, formation),
            'confidence_breakdown': self._calculate_confidence_breakdown(historical_matches, formation)
        }
        
        prediction['prediction_confidence'] = self._calculate_overall_confidence(prediction)
        
        self.logger.info(f"Match prediction generated for {opponent.name}: {prediction['predicted_outcome']['most_likely']}")
        return prediction
    
    def predict_player_performance(self, player, opponent=None, formation=None, days=60):
        if not isinstance(player, Player):
            raise ValidationError("Invalid player object provided")
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        base_stats = PlayerStats.objects.filter(
            player=player,
            match__scheduled_datetime__gte=cutoff_date,
            match__status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if not base_stats.exists():
            raise InsufficientDataError(f"Insufficient data for {player.full_name} performance prediction")
        
        opponent_specific_stats = base_stats.filter(match__opponent=opponent) if opponent else base_stats
        
        prediction = {
            'player_id': str(player.id),
            'player_name': player.full_name,
            'position': player.position,
            'analysis_period': days,
            'predicted_rating': self._predict_player_rating(base_stats, opponent_specific_stats),
            'predicted_contributions': self._predict_player_contributions(base_stats, opponent_specific_stats, player.position),
            'performance_probability_ranges': self._calculate_performance_probability_ranges(base_stats),
            'form_trajectory': self._predict_form_trajectory(base_stats),
            'fitness_considerations': self._assess_fitness_impact(player),
            'opponent_specific_factors': self._analyze_opponent_specific_factors(opponent_specific_stats, opponent) if opponent else None,
            'formation_impact': self._assess_formation_impact(player, formation) if formation else None,
            'confidence_level': self._calculate_player_prediction_confidence(base_stats, opponent_specific_stats)
        }
        
        return prediction
    
    def predict_formation_effectiveness(self, formation, opponent=None, days=120):
        if not isinstance(formation, Formation):
            raise ValidationError("Invalid formation object provided")
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        formation_matches = Match.objects.filter(
            lineups__formation=formation,
            lineups__is_starting_eleven=True,
            scheduled_datetime__gte=cutoff_date,
            status__in=['COMPLETED', 'FULL_TIME']
        ).distinct()
        
        if formation_matches.count() < 3:
            return self._generate_limited_formation_prediction(formation, opponent)
        
        opponent_specific = formation_matches.filter(opponent=opponent) if opponent else formation_matches
        
        prediction = {
            'formation_name': formation.name,
            'formation_id': str(formation.id),
            'analysis_period': days,
            'matches_analyzed': formation_matches.count(),
            'effectiveness_prediction': self._predict_formation_effectiveness_score(formation_matches, opponent_specific),
            'expected_outcomes': self._predict_formation_outcomes(formation_matches, opponent_specific),
            'tactical_advantages': self._identify_tactical_advantages(formation, formation_matches, opponent),
            'potential_vulnerabilities': self._identify_formation_vulnerabilities(formation, formation_matches, opponent),
            'player_suitability': self._assess_current_squad_suitability(formation),
            'situational_effectiveness': self._predict_situational_effectiveness(formation, formation_matches, opponent),
            'confidence_rating': self._calculate_formation_prediction_confidence(formation_matches, opponent_specific)
        }
        
        return prediction
    
    def predict_season_trajectory(self, months_ahead=6):
        recent_months = timezone.now() - timedelta(days=90)
        
        recent_matches = Match.objects.filter(
            scheduled_datetime__gte=recent_months,
            status__in=['COMPLETED', 'FULL_TIME']
        )
        
        if recent_matches.count() < 5:
            raise InsufficientDataError("Insufficient recent data for season trajectory prediction")
        
        trajectory = {
            'analysis_period': '90 days',
            'projection_period': f'{months_ahead} months',
            'current_form_analysis': self._analyze_current_form(recent_matches),
            'projected_performance_trends': self._project_performance_trends(recent_matches, months_ahead),
            'goal_scoring_projections': self._project_goal_scoring_trends(recent_matches, months_ahead),
            'defensive_projections': self._project_defensive_trends(recent_matches, months_ahead),
            'player_development_projections': self._project_player_development(months_ahead),
            'potential_scenarios': self._generate_scenario_predictions(recent_matches, months_ahead),
            'key_improvement_areas': self._identify_improvement_opportunities(recent_matches),
            'risk_factors': self._identify_trajectory_risks(recent_matches),
            'confidence_level': self._calculate_trajectory_confidence(recent_matches)
        }
        
        return trajectory
    
    def _calculate_outcome_probabilities(self, historical_matches, formation):
        total_matches = historical_matches.count()
        wins = historical_matches.filter(result='WIN').count()
        draws = historical_matches.filter(result='DRAW').count()
        losses = historical_matches.filter(result='LOSS').count()
        
        base_probabilities = {
            'win': (wins / total_matches) * 100,
            'draw': (draws / total_matches) * 100,
            'loss': (losses / total_matches) * 100
        }
        
        if formation:
            formation_adjustment = self._get_formation_outcome_adjustment(formation, historical_matches)
            for outcome in base_probabilities:
                base_probabilities[outcome] += formation_adjustment.get(outcome, 0)
        
        current_form_adjustment = self._get_current_form_adjustment(historical_matches)
        for outcome in base_probabilities:
            base_probabilities[outcome] += current_form_adjustment.get(outcome, 0)
        
        total_prob = sum(base_probabilities.values())
        if total_prob > 0:
            normalized_probabilities = {k: round((v/total_prob) * 100, 1) for k, v in base_probabilities.items()}
        else:
            normalized_probabilities = {'win': 33.3, 'draw': 33.3, 'loss': 33.4}
        
        most_likely = max(normalized_probabilities.items(), key=lambda x: x[1])
        
        return {
            'win_probability': normalized_probabilities['win'],
            'draw_probability': normalized_probabilities['draw'],
            'loss_probability': normalized_probabilities['loss'],
            'most_likely': most_likely[0],
            'confidence': round(most_likely[1], 1)
        }
    
    def _predict_scoreline(self, historical_matches, formation):
        goals_scored = [match.chelsea_score for match in historical_matches]
        goals_conceded = [match.opponent_score for match in historical_matches]
        
        avg_goals_scored = sum(goals_scored) / len(goals_scored)
        avg_goals_conceded = sum(goals_conceded) / len(goals_conceded)
        
        if formation:
            formation_modifier = self._get_formation_scoring_modifier(formation, historical_matches)
            avg_goals_scored += formation_modifier['attacking']
            avg_goals_conceded += formation_modifier['defensive']
        
        predicted_chelsea_goals = max(0, round(avg_goals_scored))
        predicted_opponent_goals = max(0, round(avg_goals_conceded))
        
        return {
            'predicted_score': f"{predicted_chelsea_goals}-{predicted_opponent_goals}",
            'chelsea_goals_expected': predicted_chelsea_goals,
            'opponent_goals_expected': predicted_opponent_goals,
            'goal_difference_expected': predicted_chelsea_goals - predicted_opponent_goals,
            'scoring_confidence': self._calculate_scoring_confidence(goals_scored, goals_conceded)
        }
    
    def _identify_key_prediction_factors(self, historical_matches, formation):
        factors = []
        
        recent_form = historical_matches.order_by('-scheduled_datetime')[:3]
        recent_wins = recent_form.filter(result='WIN').count()
        
        if recent_wins >= 2:
            factors.append({
                'factor': 'Positive recent form',
                'impact': 'Favourable',
                'weight': 'High'
            })
        elif recent_wins == 0:
            factors.append({
                'factor': 'Poor recent form',
                'impact': 'Concerning',
                'weight': 'High'
            })
        
        home_matches = historical_matches.filter(is_home=True)
        away_matches = historical_matches.filter(is_home=False)
        
        if home_matches.exists() and away_matches.exists():
            home_win_rate = (home_matches.filter(result='WIN').count() / home_matches.count()) * 100
            away_win_rate = (away_matches.filter(result='WIN').count() / away_matches.count()) * 100
            
            if home_win_rate > away_win_rate + 25:
                factors.append({
                    'factor': 'Strong home advantage',
                    'impact': 'Venue dependent',
                    'weight': 'Medium'
                })
        
        if formation:
            formation_effectiveness = self._calculate_formation_historical_effectiveness(formation)
            if formation_effectiveness > 75:
                factors.append({
                    'factor': 'Tactically suited formation',
                    'impact': 'Favourable',
                    'weight': 'Medium'
                })
        
        return factors
    
    def _assess_match_risks(self, historical_matches, opponent):
        risks = []
        
        high_scoring_against = historical_matches.filter(opponent_score__gte=3).count()
        if high_scoring_against / historical_matches.count() > 0.3:
            risks.append({
                'risk': 'Opponent capable of high-scoring performances',
                'probability': 'Medium',
                'mitigation': 'Focus on defensive organisation'
            })
        
        recent_losses = historical_matches.order_by('-scheduled_datetime')[:5].filter(result='LOSS').count()
        if recent_losses >= 3:
            risks.append({
                'risk': 'Recent poor record against this opponent',
                'probability': 'High',
                'mitigation': 'Tactical approach review required'
            })
        
        clean_sheet_rate = historical_matches.filter(opponent_score=0).count() / historical_matches.count()
        if clean_sheet_rate < 0.2:
            risks.append({
                'risk': 'Difficulty keeping clean sheets',
                'probability': 'Medium',
                'mitigation': 'Strengthen defensive transitions'
            })
        
        return risks
    
    def _generate_tactical_predictions(self, historical_matches, opponent, formation):
        predictions = []
        
        if opponent.typical_formation:
            predictions.append({
                'aspect': 'Formation matchup',
                'prediction': f"Expect {opponent.typical_formation} from opponent",
                'tactical_response': self._suggest_formation_counter(opponent.typical_formation, formation)
            })
        
        avg_possession = self._calculate_average_possession_against_opponent(historical_matches)
        if avg_possession:
            if avg_possession > 60:
                predictions.append({
                    'aspect': 'Possession control',
                    'prediction': 'Likely to dominate possession',
                    'tactical_response': 'Focus on patient build-up play'
                })
            elif avg_possession < 45:
                predictions.append({
                    'aspect': 'Possession battle',
                    'prediction': 'Opponent may dominate possession',
                    'tactical_response': 'Prepare for counter-attacking opportunities'
                })
        
        return predictions
    
    def _predict_player_impacts(self, historical_matches, formation):
        impacts = []
        
        active_players = Player.objects.filter(is_active=True, is_injured=False)
        
        for player in active_players[:5]:
            recent_stats = PlayerStats.objects.filter(
                player=player,
                match__in=historical_matches
            )
            
            if recent_stats.exists():
                avg_rating = recent_stats.aggregate(avg=Avg('rating'))['avg']
                total_contributions = recent_stats.aggregate(
                    goals=Sum('goals'),
                    assists=Sum('assists')
                )
                
                if avg_rating and avg_rating > 7:
                    impacts.append({
                        'player': player.full_name,
                        'position': player.position,
                        'predicted_impact': 'High',
                        'expected_rating': round(avg_rating, 1),
                        'key_contributions': f"{total_contributions['goals'] or 0}G, {total_contributions['assists'] or 0}A in recent matches"
                    })
        
        return impacts[:3]
    
    def _calculate_confidence_breakdown(self, historical_matches, formation):
        breakdown = {
            'data_quality': min(100, historical_matches.count() * 20),
            'recent_form_stability': self._assess_form_stability(historical_matches),
            'tactical_certainty': 80 if formation else 60,
            'historical_consistency': self._calculate_historical_consistency(historical_matches)
        }
        
        return breakdown
    
    def _predict_player_rating(self, base_stats, opponent_specific_stats):
        base_avg = base_stats.aggregate(avg=Avg('rating'))['avg'] or 6.0
        
        if opponent_specific_stats.exists():
            opponent_avg = opponent_specific_stats.aggregate(avg=Avg('rating'))['avg'] or base_avg
            weighted_prediction = (base_avg * 0.7) + (opponent_avg * 0.3)
        else:
            weighted_prediction = base_avg
        
        recent_trend = self._calculate_recent_trend(base_stats)
        adjusted_prediction = weighted_prediction + recent_trend
        
        final_prediction = max(1.0, min(10.0, adjusted_prediction))
        
        return {
            'predicted_rating': round(final_prediction, 1),
            'confidence_range': {
                'low': round(max(1.0, final_prediction - 0.8), 1),
                'high': round(min(10.0, final_prediction + 0.8), 1)
            },
            'prediction_basis': 'Historical average with recent form adjustment'
        }
    
    def _predict_player_contributions(self, base_stats, opponent_specific_stats, position):
        base_contributions = base_stats.aggregate(
            avg_goals=Avg('goals'),
            avg_assists=Avg('assists'),
            avg_tackles=Avg('tackles'),
            avg_passes_completed=Avg('passes_completed')
        )
        
        contributions = {
            'goals': round(base_contributions['avg_goals'] or 0, 2),
            'assists': round(base_contributions['avg_assists'] or 0, 2)
        }
        
        if position in ['CB', 'CDM', 'LB', 'RB']:
            contributions['defensive_actions'] = round(base_contributions['avg_tackles'] or 0, 1)
        
        if position in ['CM', 'CAM', 'CDM']:
            contributions['passes_completed'] = round(base_contributions['avg_passes_completed'] or 0, 0)
        
        return contributions
    
    def _calculate_performance_probability_ranges(self, base_stats):
        ratings = [float(stat.rating) for stat in base_stats]
        
        if len(ratings) < 3:
            return {'insufficient_data': True}
        
        excellent_performances = len([r for r in ratings if r >= 8.0])
        good_performances = len([r for r in ratings if 7.0 <= r < 8.0])
        average_performances = len([r for r in ratings if 6.0 <= r < 7.0])
        poor_performances = len([r for r in ratings if r < 6.0])
        
        total = len(ratings)
        
        return {
            'excellent_performance_probability': round((excellent_performances / total) * 100, 1),
            'good_performance_probability': round((good_performances / total) * 100, 1),
            'average_performance_probability': round((average_performances / total) * 100, 1),
            'poor_performance_probability': round((poor_performances / total) * 100, 1)
        }
    
    def _predict_form_trajectory(self, base_stats):
        recent_ratings = [float(stat.rating) for stat in base_stats.order_by('-match__scheduled_datetime')[:5]]
        
        if len(recent_ratings) < 3:
            return {'insufficient_data': True}
        
        trend = self._calculate_rating_trend(recent_ratings)
        
        if trend > 0.3:
            trajectory = 'Improving'
        elif trend < -0.3:
            trajectory = 'Declining'
        else:
            trajectory = 'Stable'
        
        return {
            'trajectory': trajectory,
            'trend_strength': round(abs(trend), 2),
            'next_match_expectation': self._predict_next_match_rating(recent_ratings, trend)
        }
    
    def _assess_fitness_impact(self, player):
        fitness_level = player.fitness_level
        
        if fitness_level >= 95:
            impact = 'Positive - peak fitness'
        elif fitness_level >= 85:
            impact = 'Neutral - good fitness'
        elif fitness_level >= 75:
            impact = 'Slight concern - monitor stamina'
        else:
            impact = 'Significant concern - fitness issues'
        
        return {
            'current_fitness': fitness_level,
            'impact_assessment': impact,
            'injury_status': player.is_injured,
            'fitness_trend': self._assess_fitness_trend(player)
        }
    
    def _analyze_opponent_specific_factors(self, opponent_stats, opponent):
        if not opponent_stats.exists():
            return {'insufficient_opponent_specific_data': True}
        
        opponent_avg = opponent_stats.aggregate(avg=Avg('rating'))['avg']
        general_avg = 6.5
        
        opponent_performance_modifier = opponent_avg - general_avg
        
        return {
            'opponent_specific_rating': round(opponent_avg, 2),
            'performance_modifier': round(opponent_performance_modifier, 2),
            'matches_against_opponent': opponent_stats.count(),
            'historical_effectiveness': 'Strong' if opponent_performance_modifier > 0.5 else 'Weak' if opponent_performance_modifier < -0.5 else 'Average'
        }
    
    def _assess_formation_impact(self, player, formation):
        position_suitability = self._assess_position_suitability_in_formation(player.position, formation.name)
        
        return {
            'formation_name': formation.name,
            'position_suitability': position_suitability,
            'expected_role': self._predict_player_role_in_formation(player.position, formation.name),
            'tactical_freedom': self._assess_tactical_freedom(player.position, formation.name)
        }
    
    def _calculate_player_prediction_confidence(self, base_stats, opponent_specific_stats):
        data_points = base_stats.count()
        opponent_data_points = opponent_specific_stats.count() if opponent_specific_stats else 0
        
        data_confidence = min(100, data_points * 15)
        opponent_confidence = min(50, opponent_data_points * 20)
        
        overall_confidence = (data_confidence * 0.7) + (opponent_confidence * 0.3)
        
        return round(overall_confidence, 1)
    
    def _generate_limited_prediction(self, opponent, formation):
        return {
            'opponent': opponent.name,
            'prediction_type': 'Limited data prediction',
            'predicted_outcome': {
                'win_probability': 40.0,
                'draw_probability': 30.0,
                'loss_probability': 30.0,
                'most_likely': 'win',
                'confidence': 25.0
            },
            'predicted_scoreline': {
                'predicted_score': '2-1',
                'chelsea_goals_expected': 2,
                'opponent_goals_expected': 1,
                'scoring_confidence': 30.0
            },
            'data_limitation': 'Insufficient historical data for comprehensive prediction',
            'recommendation': 'Focus on general tactical preparation and squad fitness'
        }
    
    def _generate_limited_formation_prediction(self, formation, opponent):
        return {
            'formation_name': formation.name,
            'prediction_type': 'Limited data prediction',
            'effectiveness_prediction': {
                'predicted_effectiveness': 65.0,
                'confidence': 30.0
            },
            'data_limitation': 'Insufficient recent usage for accurate prediction',
            'general_assessment': self._get_formation_general_assessment(formation.name)
        }
    
    def _predict_formation_effectiveness_score(self, formation_matches, opponent_specific):
        base_effectiveness = self._calculate_historical_formation_effectiveness(formation_matches)
        
        if opponent_specific.exists():
            opponent_effectiveness = self._calculate_historical_formation_effectiveness(opponent_specific)
            weighted_effectiveness = (base_effectiveness * 0.7) + (opponent_effectiveness * 0.3)
        else:
            weighted_effectiveness = base_effectiveness
        
        return {
            'predicted_effectiveness': round(weighted_effectiveness, 1),
            'confidence': self._calculate_formation_effectiveness_confidence(formation_matches, opponent_specific)
        }
    
    def _predict_formation_outcomes(self, formation_matches, opponent_specific):
        if opponent_specific.exists():
            analysis_matches = opponent_specific
        else:
            analysis_matches = formation_matches.order_by('-scheduled_datetime')[:10]
        
        wins = analysis_matches.filter(result='WIN').count()
        total = analysis_matches.count()
        
        win_rate = (wins / total) * 100 if total > 0 else 50
        
        return {
            'expected_win_rate': round(win_rate, 1),
            'expected_result': 'Win' if win_rate > 60 else 'Draw' if win_rate > 40 else 'Loss risk',
            'based_on_matches': total
        }
    
    def _identify_tactical_advantages(self, formation, formation_matches, opponent):
        advantages = []
        
        avg_goals = sum(match.chelsea_score for match in formation_matches) / formation_matches.count()
        if avg_goals > 2.0:
            advantages.append('Strong attacking output')
        
        clean_sheets = formation_matches.filter(opponent_score=0).count()
        clean_sheet_rate = (clean_sheets / formation_matches.count()) * 100
        if clean_sheet_rate > 40:
            advantages.append('Solid defensive record')
        
        if '3' in formation.name:
            advantages.append('Attacking wing-backs provide width')
        elif '4' in formation.name:
            advantages.append('Balanced defensive structure')
        
        return advantages
    
    def _identify_formation_vulnerabilities(self, formation, formation_matches, opponent):
        vulnerabilities = []
        
        high_conceding_matches = formation_matches.filter(opponent_score__gte=2).count()
        if (high_conceding_matches / formation_matches.count()) > 0.4:
            vulnerabilities.append('Susceptible to conceding multiple goals')
        
        away_matches = formation_matches.filter(is_home=False)
        if away_matches.exists():
            away_win_rate = (away_matches.filter(result='WIN').count() / away_matches.count()) * 100
            if away_win_rate < 30:
                vulnerabilities.append('Struggles in away matches')
        
        if '3' in formation.name:
            vulnerabilities.append('Potential vulnerability to wide attacks')
        
        return vulnerabilities
    
    def _assess_current_squad_suitability(self, formation):
        available_players = Player.objects.filter(is_active=True, is_injured=False)
        
        position_requirements = self._get_formation_position_requirements(formation.name)
        suitability_score = 0
        total_positions = len(position_requirements)
        
        for position, required_count in position_requirements.items():
            available_count = available_players.filter(position=position).count()
            if available_count >= required_count:
                suitability_score += 1
        
        suitability_percentage = (suitability_score / total_positions) * 100
        
        return {
            'suitability_score': round(suitability_percentage, 1),
            'assessment': 'High' if suitability_percentage > 80 else 'Medium' if suitability_percentage > 60 else 'Low',
            'missing_positions': [pos for pos, req in position_requirements.items() 
                                if available_players.filter(position=pos).count() < req]
        }
    
    def _predict_situational_effectiveness(self, formation, formation_matches, opponent):
        situations = {}
        
        home_matches = formation_matches.filter(is_home=True)
        away_matches = formation_matches.filter(is_home=False)
        
        if home_matches.exists():
            home_effectiveness = (home_matches.filter(result='WIN').count() / home_matches.count()) * 100
            situations['home_effectiveness'] = round(home_effectiveness, 1)
        
        if away_matches.exists():
            away_effectiveness = (away_matches.filter(result='WIN').count() / away_matches.count()) * 100
            situations['away_effectiveness'] = round(away_effectiveness, 1)
        
        return situations
    
    def _calculate_formation_prediction_confidence(self, formation_matches, opponent_specific):
        base_confidence = min(80, formation_matches.count() * 15)
        
        if opponent_specific and opponent_specific.exists():
            opponent_confidence = min(40, opponent_specific.count() * 20)
        else:
            opponent_confidence = 20
        
        overall_confidence = (base_confidence * 0.7) + (opponent_confidence * 0.3)
        
        return round(overall_confidence, 1)
    
    def _analyze_current_form(self, recent_matches):
        total_matches = recent_matches.count()
        wins = recent_matches.filter(result='WIN').count()
        
        form_rating = (wins / total_matches) * 100 if total_matches > 0 else 0
        
        return {
            'matches_analyzed': total_matches,
            'win_rate': round(form_rating, 1),
            'form_assessment': 'Excellent' if form_rating > 75 else 'Good' if form_rating > 60 else 'Average' if form_rating > 40 else 'Poor'
        }
    
    def _project_performance_trends(self, recent_matches, months_ahead):
        current_trend = self._calculate_performance_trend(recent_matches)
        
        if current_trend > 0:
            projection = 'Continued improvement expected'
        elif current_trend < -0.2:
            projection = 'Performance decline risk'
        else:
            projection = 'Stable performance expected'
        
        return {
            'projection': projection,
            'trend_strength': round(abs(current_trend), 2),
            'projection_confidence': 60 if abs(current_trend) > 0.1 else 40
        }
    
    def _project_goal_scoring_trends(self, recent_matches, months_ahead):
        recent_goals = [match.chelsea_score for match in recent_matches]
        avg_goals = sum(recent_goals) / len(recent_goals)
        
        trend = self._calculate_scoring_trend(recent_goals)
        projected_avg = max(0, avg_goals + (trend * months_ahead * 0.1))
        
        return {
            'current_average': round(avg_goals, 2),
            'projected_average': round(projected_avg, 2),
            'trend': 'Improving' if trend > 0.1 else 'Declining' if trend < -0.1 else 'Stable'
        }
    
    def _project_defensive_trends(self, recent_matches, months_ahead):
        recent_conceded = [match.opponent_score for match in recent_matches]
        avg_conceded = sum(recent_conceded) / len(recent_conceded)
        
        trend = self._calculate_defensive_trend(recent_conceded)
        projected_avg = max(0, avg_conceded + (trend * months_ahead * 0.1))
        
        return {
            'current_average': round(avg_conceded, 2),
            'projected_average': round(projected_avg, 2),
            'trend': 'Improving' if trend < -0.1 else 'Declining' if trend > 0.1 else 'Stable'
        }
    
    def _project_player_development(self, months_ahead):
        young_players = Player.objects.filter(
            is_active=True,
            date_of_birth__gte=timezone.now().date() - timedelta(days=365*23)
        )
        
        development_projections = []
        
        for player in young_players[:5]:
            recent_stats = PlayerStats.objects.filter(
                player=player,
                match__scheduled_datetime__gte=timezone.now() - timedelta(days=60)
            )
            
            if recent_stats.exists():
                current_avg = recent_stats.aggregate(avg=Avg('rating'))['avg']
                projected_improvement = min(0.5, months_ahead * 0.05)
                
                development_projections.append({
                    'player': player.full_name,
                    'current_rating': round(current_avg, 1),
                    'projected_rating': round(current_avg + projected_improvement, 1),
                    'development_potential': 'High' if projected_improvement > 0.3 else 'Medium'
                })
        
        return development_projections
    
    def _generate_scenario_predictions(self, recent_matches, months_ahead):
        scenarios = {}
        
        current_form = self._analyze_current_form(recent_matches)
        
        if current_form['win_rate'] > 60:
            scenarios['optimistic'] = 'Continued strong performance, potential trophy challenge'
            scenarios['realistic'] = 'Consistent performance with occasional setbacks'
            scenarios['pessimistic'] = 'Form dip due to player fatigue or tactical adjustments'
        else:
            scenarios['optimistic'] = 'Significant improvement with tactical changes'
            scenarios['realistic'] = 'Gradual improvement over time'
            scenarios['pessimistic'] = 'Continued struggles without major changes'
        
        return scenarios
    
    def _identify_improvement_opportunities(self, recent_matches):
        opportunities = []
        
        avg_goals = sum(match.chelsea_score for match in recent_matches) / recent_matches.count()
        if avg_goals < 2.0:
            opportunities.append('Attacking efficiency - improve chance conversion')
        
        avg_conceded = sum(match.opponent_score for match in recent_matches) / recent_matches.count()
        if avg_conceded > 1.5:
            opportunities.append('Defensive solidity - reduce goals conceded')
        
        return opportunities
    
    def _identify_trajectory_risks(self, recent_matches):
        risks = []
        
        recent_form = recent_matches.order_by('-scheduled_datetime')[:5]
        recent_wins = recent_form.filter(result='WIN').count()
        
        if recent_wins <= 1:
            risks.append('Poor recent form may impact confidence')
        
        return risks
    
    def _calculate_trajectory_confidence(self, recent_matches):
        data_quality = min(80, recent_matches.count() * 15)
        form_stability = self._assess_form_stability(recent_matches)
        
        confidence = (data_quality * 0.6) + (form_stability * 0.4)
        return round(confidence, 1)
    
    def _calculate_overall_confidence(self, prediction):
        confidence_factors = prediction.get('confidence_breakdown', {})
        
        if confidence_factors:
            total_confidence = sum(confidence_factors.values()) / len(confidence_factors)
        else:
            total_confidence = 50
        
        return round(total_confidence, 1)
    
    def _get_formation_outcome_adjustment(self, formation, historical_matches):
        formation_matches = historical_matches.filter(lineups__formation=formation, lineups__is_starting_eleven=True)
        
        if formation_matches.count() < 2:
            return {'win': 0, 'draw': 0, 'loss': 0}
        
        formation_win_rate = (formation_matches.filter(result='WIN').count() / formation_matches.count()) * 100
        overall_win_rate = (historical_matches.filter(result='WIN').count() / historical_matches.count()) * 100
        
        adjustment = formation_win_rate - overall_win_rate
        
        return {
            'win': adjustment,
            'draw': 0,
            'loss': -adjustment
        }
    
    def _get_current_form_adjustment(self, historical_matches):
        recent_five = historical_matches.order_by('-scheduled_datetime')[:5]
        recent_wins = recent_five.filter(result='WIN').count()
        
        form_factor = (recent_wins / 5) * 100
        
        if form_factor > 80:
            return {'win': 10, 'draw': 0, 'loss': -10}
        elif form_factor < 20:
            return {'win': -10, 'draw': 0, 'loss': 10}
        else:
            return {'win': 0, 'draw': 0, 'loss': 0}
    
    def _get_formation_scoring_modifier(self, formation, historical_matches):
        formation_matches = historical_matches.filter(lineups__formation=formation, lineups__is_starting_eleven=True)
        
        if not formation_matches.exists():
            return {'attacking': 0, 'defensive': 0}
        
        formation_goals = sum(match.chelsea_score for match in formation_matches) / formation_matches.count()
        overall_goals = sum(match.chelsea_score for match in historical_matches) / historical_matches.count()
        
        formation_conceded = sum(match.opponent_score for match in formation_matches) / formation_matches.count()
        overall_conceded = sum(match.opponent_score for match in historical_matches) / historical_matches.count()
        
        return {
            'attacking': formation_goals - overall_goals,
            'defensive': formation_conceded - overall_conceded
        }
    
    def _calculate_scoring_confidence(self, goals_scored, goals_conceded):
        if len(goals_scored) < 3:
            return 30.0
        
        goal_variance = self._calculate_variance(goals_scored)
        conceded_variance = self._calculate_variance(goals_conceded)
        
        confidence = max(30, 80 - (goal_variance * 10) - (conceded_variance * 10))
        return round(confidence, 1)
    
    def _calculate_variance(self, values):
        if len(values) <= 1:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _assess_form_stability(self, matches):
        results = [1 if match.result == 'WIN' else 0.5 if match.result == 'DRAW' else 0 for match in matches.order_by('-scheduled_datetime')[:10]]
        
        if len(results) < 3:
            return 50
        
        variance = self._calculate_variance(results)
        stability = max(0, 100 - (variance * 100))
        
        return round(stability, 1)
    
    def _calculate_historical_consistency(self, matches):
        results = [match.result for match in matches]
        wins = results.count('WIN')
        total = len(results)
        
        win_rate = (wins / total) * 100 if total > 0 else 0
        
        if 40 <= win_rate <= 70:
            return 80
        elif 30 <= win_rate <= 80:
            return 60
        else:
            return 40
    
    def _calculate_recent_trend(self, stats):
        if stats.count() < 5:
            return 0
        
        recent_ratings = [float(stat.rating) for stat in stats.order_by('-match__scheduled_datetime')[:5]]
        older_ratings = [float(stat.rating) for stat in stats.order_by('-match__scheduled_datetime')[5:10]]
        
        if not older_ratings:
            return 0
        
        recent_avg = sum(recent_ratings) / len(recent_ratings)
        older_avg = sum(older_ratings) / len(older_ratings)
        
        return recent_avg - older_avg
    
    def _calculate_rating_trend(self, ratings):
        if len(ratings) < 3:
            return 0
        
        recent_avg = sum(ratings[:2]) / 2
        earlier_avg = sum(ratings[-2:]) / 2
        
        return recent_avg - earlier_avg
    
    def _predict_next_match_rating(self, recent_ratings, trend):
        base_prediction = recent_ratings[0] if recent_ratings else 6.5
        trend_adjustment = trend * 0.5
        
        prediction = max(1.0, min(10.0, base_prediction + trend_adjustment))
        
        return round(prediction, 1)
    
    def _assess_fitness_trend(self, player):
        if player.fitness_level >= 90:
            return 'Stable at high level'
        elif player.fitness_level >= 80:
            return 'Good condition'
        else:
            return 'Needs improvement'
    
    def _assess_position_suitability_in_formation(self, position, formation_name):
        formation_suitability = {
            '4-4-2': {'ST': 'High', 'LM': 'High', 'RM': 'High', 'CM': 'High', 'CB': 'High', 'LB': 'High', 'RB': 'High', 'GK': 'High'},
            '4-3-3': {'ST': 'High', 'LW': 'High', 'RW': 'High', 'CM': 'High', 'CDM': 'High', 'CB': 'High', 'LB': 'High', 'RB': 'High', 'GK': 'High'},
            '3-5-2': {'ST': 'High', 'CAM': 'High', 'CDM': 'High', 'LM': 'Medium', 'RM': 'Medium', 'CB': 'High', 'GK': 'High'}
        }
        
        return formation_suitability.get(formation_name, {}).get(position, 'Medium')
    
    def _predict_player_role_in_formation(self, position, formation_name):
        role_mapping = {
            '4-4-2': {
                'ST': 'Primary goalscorer',
                'LM': 'Width and crosses',
                'RM': 'Width and crosses',
                'CM': 'Box-to-box midfielder'
            },
            '4-3-3': {
                'ST': 'Central striker',
                'LW': 'Inside forward',
                'RW': 'Inside forward',
                'CM': 'Creative midfielder',
                'CDM': 'Defensive anchor'
            }
        }
        
        return role_mapping.get(formation_name, {}).get(position, 'Standard role')
    
    def _assess_tactical_freedom(self, position, formation_name):
        freedom_levels = {
            '4-4-2': {'ST': 'High', 'LM': 'Medium', 'RM': 'Medium', 'CM': 'High'},
            '4-3-3': {'ST': 'High', 'LW': 'High', 'RW': 'High', 'CAM': 'High', 'CDM': 'Low'},
            '3-5-2': {'ST': 'High', 'CAM': 'High', 'LM': 'Medium', 'RM': 'Medium'}
        }
        
        return freedom_levels.get(formation_name, {}).get(position, 'Medium')
    
    def _calculate_formation_historical_effectiveness(self, formation_matches):
        if not formation_matches.exists():
            return 50
        
        wins = formation_matches.filter(result='WIN').count()
        draws = formation_matches.filter(result='DRAW').count()
        total = formation_matches.count()
        
        points = (wins * 3) + draws
        points_per_match = points / total
        
        effectiveness = (points_per_match / 3) * 100
        
        return round(effectiveness, 1)
    
    def _calculate_formation_effectiveness_confidence(self, formation_matches, opponent_specific):
        base_confidence = min(80, formation_matches.count() * 12)
        
        if opponent_specific and opponent_specific.exists():
            opponent_boost = min(30, opponent_specific.count() * 15)
        else:
            opponent_boost = 0
        
        return round(base_confidence + opponent_boost, 1)
    
    def _get_formation_general_assessment(self, formation_name):
        assessments = {
            '4-4-2': 'Balanced formation with good defensive stability',
            '4-3-3': 'Attacking formation with wide threat',
            '3-5-2': 'Flexible formation with attacking wing-backs',
            '5-3-2': 'Defensive formation suitable for counter-attacks'
        }
        
        return assessments.get(formation_name, 'Standard tactical approach')
    
    def _get_formation_position_requirements(self, formation_name):
        requirements = {
            '4-4-2': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CM': 2, 'LM': 1, 'RM': 1, 'ST': 2},
            '4-3-3': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 1, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 1},
            '3-5-2': {'GK': 1, 'CB': 3, 'LM': 1, 'RM': 1, 'CDM': 1, 'CM': 2, 'ST': 2}
        }
        
        return requirements.get(formation_name, {})
    
    def _suggest_formation_counter(self, opponent_formation, our_formation):
        counter_suggestions = {
            '4-4-2': 'Use wide players to exploit flanks',
            '4-3-3': 'Strengthen midfield to match their numerical advantage',
            '3-5-2': 'Target wide areas where they may be vulnerable'
        }
        
        return counter_suggestions.get(opponent_formation, 'Standard tactical approach')
    
    def _calculate_average_possession_against_opponent(self, matches):
        possession_values = []
        
        for match in matches:
            try:
                team_stats = TeamStats.objects.get(match=match)
                if team_stats.possession_percentage:
                    possession_values.append(float(team_stats.possession_percentage))
            except TeamStats.DoesNotExist:
                continue
        
        if not possession_values:
            return None
        
        return sum(possession_values) / len(possession_values)
    
    def _calculate_performance_trend(self, matches):
        results = [1 if match.result == 'WIN' else 0.5 if match.result == 'DRAW' else 0 for match in matches.order_by('scheduled_datetime')]
        
        if len(results) < 4:
            return 0
        
        recent_half = results[len(results)//2:]
        early_half = results[:len(results)//2]
        
        recent_avg = sum(recent_half) / len(recent_half)
        early_avg = sum(early_half) / len(early_half)
        
        return recent_avg - early_avg
    
    def _calculate_scoring_trend(self, goals):
        if len(goals) < 4:
            return 0
        
        recent_half = goals[len(goals)//2:]
        early_half = goals[:len(goals)//2]
        
        recent_avg = sum(recent_half) / len(recent_half)
        early_avg = sum(early_half) / len(early_half)
        
        return recent_avg - early_avg
    
    def _calculate_defensive_trend(self, goals_conceded):
        if len(goals_conceded) < 4:
            return 0
        
        recent_half = goals_conceded[len(goals_conceded)//2:]
        early_half = goals_conceded[:len(goals_conceded)//2]
        
        recent_avg = sum(recent_half) / len(recent_half)
        early_avg = sum(early_half) / len(early_half)
        
        return recent_avg - early_avg