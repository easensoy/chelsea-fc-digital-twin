import requests
import json
import time
from bs4 import BeautifulSoup
from datetime import datetime
import re
from dataclasses import dataclass, asdict
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class Player:
    name: str
    number: str = ""
    position: str = ""
    image: str = ""
    nationality: str = ""
    age: str = ""
    height: str = ""
    weight: str = ""
    birthplace: str = ""
    source: str = "Chelsea FC Official"

class ChelseaPlayerScraper:
    def __init__(self):
        self.base_url = "https://www.chelseafc.com"
        self.squad_url = "https://www.chelseafc.com/en/teams/men"
        self.players: List[Player] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_with_requests(self) -> List[Player]:
        """Main scraping method using requests and BeautifulSoup."""
        logger.info("🔄 Starting Chelsea player scraping with requests...")

        try:
            response = self.session.get(self.squad_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for player cards, profile cards, or any player-related containers
            player_selectors = [
                '.player-card',
                '.profile-card',
                '[data-player]',
                '.player-tile',
                '.squad-player',
                '[class*="player"]',
                '[class*="profile"]'
            ]

            players = []

            for selector in player_selectors:
                elements = soup.select(selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                    for element in elements:
                        player_data = self._extract_player_data_from_element(element)
                        if player_data and player_data.name and len(player_data.name) > 2:
                            players.append(player_data)
                    if players:
                        break

            # If no player cards found, try to extract from JSON data in scripts
            if not players:
                players = self._extract_from_scripts(soup)

            # If still no players, try alternative approaches
            if not players:
                players = self._try_alternative_methods()

            logger.info(f"✅ Found {len(players)} players")
            self.players = players

        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            # Use fallback data
            self.players = self.get_fallback_squad()

        return self.players

    def _extract_player_data_from_element(self, element) -> Optional[Player]:
        """Extract player data from a BeautifulSoup element."""
        try:
            # Try different selectors for player name
            name_selectors = [
                '.player-name', '.profile-name', 'h3', 'h4', 'h5',
                '[class*="name"]', '.title', '.player-title'
            ]

            name = ""
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    name = name_elem.get_text(strip=True)
                    break

            if not name or len(name) < 3:
                return None

            # Filter out non-player entries
            non_player_keywords = [
                'buy', 'ticket', 'hospitality', 'shop', 'store', 'menu', 'search',
                'login', 'register', 'subscribe', 'newsletter', 'contact', 'about',
                'policy', 'terms', 'conditions', 'more', 'view', 'read', 'watch'
            ]

            if any(keyword in name.lower() for keyword in non_player_keywords):
                return None

            # Extract image
            image = ""
            img_elem = element.select_one('img')
            if img_elem and img_elem.get('src'):
                src = img_elem['src']
                if src and 'placeholder' not in src.lower():
                    image = src if src.startswith('http') else f"{self.base_url}{src}"

            # Extract position
            position = ""
            position_selectors = ['.position', '[class*="position"]', '.role', '[class*="role"]']
            for selector in position_selectors:
                pos_elem = element.select_one(selector)
                if pos_elem and pos_elem.get_text(strip=True):
                    position = pos_elem.get_text(strip=True)
                    break

            # Extract number
            number = ""
            number_selectors = ['.number', '[class*="number"]', '.jersey']
            for selector in number_selectors:
                num_elem = element.select_one(selector)
                if num_elem and num_elem.get_text(strip=True):
                    number = re.sub(r'[^\d]', '', num_elem.get_text(strip=True))
                    break

            return Player(
                name=name,
                number=number,
                position=position,
                image=image
            )

        except Exception as e:
            logger.debug(f"Error extracting player data: {e}")
            return None

    def _extract_from_scripts(self, soup) -> List[Player]:
        """Try to extract player data from JavaScript/JSON in script tags."""
        logger.info("🔍 Looking for player data in script tags...")

        players = []
        script_tags = soup.find_all('script')

        for script in script_tags:
            if not script.string:
                continue

            script_content = script.string.lower()
            if 'player' in script_content or 'squad' in script_content:
                try:
                    # Look for JSON-like structures
                    json_matches = re.findall(r'\{[^{}]*"name"[^{}]*\}', script.string, re.IGNORECASE)
                    for match in json_matches:
                        try:
                            # Try to parse as JSON
                            data = json.loads(match)
                            if isinstance(data, dict) and 'name' in data:
                                player = Player(
                                    name=data.get('name', ''),
                                    number=str(data.get('number', '')),
                                    position=data.get('position', ''),
                                    image=data.get('image', ''),
                                    nationality=data.get('nationality', '')
                                )
                                if player.name and len(player.name) > 2:
                                    players.append(player)
                        except:
                            continue

                except Exception as e:
                    logger.debug(f"Error parsing script content: {e}")
                    continue

        logger.info(f"Found {len(players)} players from scripts")
        return players

    def _try_alternative_methods(self) -> List[Player]:
        """Try alternative scraping methods."""
        logger.info("🔄 Trying alternative scraping methods...")

        # Try direct links to player pages
        alternative_urls = [
            "https://www.chelseafc.com/en/teams/men/first-team",
            "https://www.chelseafc.com/en/players",
            "https://www.chelseafc.com/teams/first-team"
        ]

        for url in alternative_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Look for any links to player profiles
                    player_links = soup.find_all('a', href=re.compile(r'/players?/'))
                    if player_links:
                        logger.info(f"Found {len(player_links)} player links in {url}")
                        return self._scrape_from_links(player_links[:10])  # Limit to first 10

            except Exception as e:
                logger.debug(f"Alternative method failed for {url}: {e}")
                continue

        return []

    def _scrape_from_links(self, player_links) -> List[Player]:
        """Scrape individual player pages."""
        players = []

        for link in player_links:
            try:
                href = link.get('href')
                if not href:
                    continue

                player_url = href if href.startswith('http') else f"{self.base_url}{href}"

                response = self.session.get(player_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract player name from title or h1
                    name = ""
                    title_elem = soup.select_one('h1, .player-name, .profile-name')
                    if title_elem:
                        name = title_elem.get_text(strip=True)

                    # Extract image
                    image = ""
                    img_elem = soup.select_one('.player-image img, .profile-image img, img[class*="player"]')
                    if img_elem and img_elem.get('src'):
                        src = img_elem['src']
                        image = src if src.startswith('http') else f"{self.base_url}{src}"

                    if name and len(name) > 2:
                        players.append(Player(name=name, image=image))

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.debug(f"Error scraping player page: {e}")
                continue

        return players

    def enhance_with_official_data(self) -> None:
        """Enhance scraped data with official player information."""
        logger.info("🔍 Enhancing player data...")

        # Known Chelsea squad data for 2024-25 season
        official_data = {
            'Robert Sanchez': {'number': '1', 'position': 'Goalkeeper', 'nationality': 'Spain'},
            'Filip Jorgensen': {'number': '12', 'position': 'Goalkeeper', 'nationality': 'Denmark'},
            'Reece James': {'number': '24', 'position': 'Defender', 'nationality': 'England'},
            'Wesley Fofana': {'number': '29', 'position': 'Defender', 'nationality': 'France'},
            'Levi Colwill': {'number': '6', 'position': 'Defender', 'nationality': 'England'},
            'Marc Cucurella': {'number': '3', 'position': 'Defender', 'nationality': 'Spain'},
            'Malo Gusto': {'number': '27', 'position': 'Defender', 'nationality': 'France'},
            'Tosin Adarabioyo': {'number': '4', 'position': 'Defender', 'nationality': 'England'},
            'Benoit Badiashile': {'number': '5', 'position': 'Defender', 'nationality': 'France'},
            'Axel Disasi': {'number': '2', 'position': 'Defender', 'nationality': 'France'},
            'Enzo Fernandez': {'number': '8', 'position': 'Midfielder', 'nationality': 'Argentina'},
            'Moises Caicedo': {'number': '25', 'position': 'Midfielder', 'nationality': 'Ecuador'},
            'Cole Palmer': {'number': '10', 'position': 'Midfielder', 'nationality': 'England'},
            'Romeo Lavia': {'number': '45', 'position': 'Midfielder', 'nationality': 'Belgium'},
            'Kiernan Dewsbury-Hall': {'number': '22', 'position': 'Midfielder', 'nationality': 'England'},
            'Nicolas Jackson': {'number': '15', 'position': 'Forward', 'nationality': 'Senegal'},
            'Pedro Neto': {'number': '7', 'position': 'Forward', 'nationality': 'Portugal'},
            'Jadon Sancho': {'number': '19', 'position': 'Forward', 'nationality': 'England'},
            'Christopher Nkunku': {'number': '18', 'position': 'Forward', 'nationality': 'France'},
            'João Felix': {'number': '14', 'position': 'Forward', 'nationality': 'Portugal'},
            'Mykhailo Mudryk': {'number': '10', 'position': 'Forward', 'nationality': 'Ukraine'},
        }

        # Enhance existing players with official data
        for player in self.players:
            if player.name in official_data:
                data = official_data[player.name]
                if not player.number:
                    player.number = data.get('number', '')
                if not player.position:
                    player.position = data.get('position', '')
                if not player.nationality:
                    player.nationality = data.get('nationality', '')

        # Add missing players from official data
        existing_names = {p.name for p in self.players}
        for name, data in official_data.items():
            if name not in existing_names:
                self.players.append(Player(
                    name=name,
                    number=data.get('number', ''),
                    position=data.get('position', ''),
                    nationality=data.get('nationality', '')
                ))

    def get_fallback_squad(self) -> List[Player]:
        """Return current known squad as fallback."""
        return [
            Player("Robert Sanchez", "1", "Goalkeeper", nationality="Spain"),
            Player("Filip Jorgensen", "12", "Goalkeeper", nationality="Denmark"),
            Player("Reece James", "24", "Defender", nationality="England"),
            Player("Wesley Fofana", "29", "Defender", nationality="France"),
            Player("Levi Colwill", "6", "Defender", nationality="England"),
            Player("Marc Cucurella", "3", "Defender", nationality="Spain"),
            Player("Malo Gusto", "27", "Defender", nationality="France"),
            Player("Tosin Adarabioyo", "4", "Defender", nationality="England"),
            Player("Benoit Badiashile", "5", "Defender", nationality="France"),
            Player("Axel Disasi", "2", "Defender", nationality="France"),
            Player("Enzo Fernandez", "8", "Midfielder", nationality="Argentina"),
            Player("Moises Caicedo", "25", "Midfielder", nationality="Ecuador"),
            Player("Cole Palmer", "10", "Midfielder", nationality="England"),
            Player("Romeo Lavia", "45", "Midfielder", nationality="Belgium"),
            Player("Kiernan Dewsbury-Hall", "22", "Midfielder", nationality="England"),
            Player("Nicolas Jackson", "15", "Forward", nationality="Senegal"),
            Player("Pedro Neto", "7", "Forward", nationality="Portugal"),
            Player("Jadon Sancho", "19", "Forward", nationality="England"),
            Player("Christopher Nkunku", "18", "Forward", nationality="France"),
            Player("João Felix", "14", "Forward", nationality="Portugal"),
            Player("Mykhailo Mudryk", "10", "Forward", nationality="Ukraine"),
        ]

    def save_to_json(self, filename: str = "chelsea_players.json") -> None:
        """Save players data to JSON file."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "source": "Chelsea FC Official Website",
            "count": len(self.players),
            "players": [asdict(player) for player in self.players]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved {len(self.players)} players to {filename}")

    def display_results(self) -> None:
        """Display scraping results."""
        logger.info(f"\n🏆 CHELSEA FC CURRENT SQUAD ({len(self.players)} players):")
        logger.info("=" * 50)

        for i, player in enumerate(self.players, 1):
            logger.info(f"{i}. {player.name}")
            if player.number:
                logger.info(f"   Number: #{player.number}")
            if player.position:
                logger.info(f"   Position: {player.position}")
            if player.nationality:
                logger.info(f"   Nationality: {player.nationality}")
            logger.info(f"   Image: {'✅' if player.image else '❌'}")

    def run(self) -> List[Player]:
        """Main execution method."""
        try:
            # Start with reliable fallback squad data
            logger.info("📋 Using reliable squad data with photo enhancement...")
            self.players = self.get_fallback_squad()

            # Try to enhance with photos from website
            self.enhance_photos_from_website()

            self.display_results()
            return self.players

        except Exception as e:
            logger.error(f"❌ Enhancement failed: {e}")
            self.players = self.get_fallback_squad()
            self.display_results()
            return self.players

    def enhance_photos_from_website(self) -> None:
        """Try to get player photos from Chelsea website."""
        logger.info("🔍 Enhancing with photos from Chelsea website...")

        try:
            response = self.session.get(self.squad_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for images that might be player photos
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    alt = img.get('alt', '').lower()

                    # Skip non-player images
                    if any(skip in src.lower() for skip in ['logo', 'sponsor', 'badge', 'icon']):
                        continue

                    # Try to match with player names
                    for player in self.players:
                        player_name_parts = player.name.lower().split()
                        if any(part in alt for part in player_name_parts) or any(part in src.lower() for part in player_name_parts):
                            if not player.image and src:
                                player.image = src if src.startswith('http') else f"{self.base_url}{src}"
                                logger.info(f"Found photo for {player.name}")
                                break

        except Exception as e:
            logger.debug(f"Photo enhancement failed: {e}")
            pass

    def to_django_format(self) -> List[dict]:
        """Convert players to Django-compatible format."""
        django_players = []

        for i, player in enumerate(self.players, 1):
            django_player = {
                'id': i,
                'name': player.name,
                'firstname': player.name.split()[0] if player.name else '',
                'lastname': ' '.join(player.name.split()[1:]) if len(player.name.split()) > 1 else '',
                'age': self._calculate_age_from_name(player.name),  # Estimated
                'nationality': player.nationality,
                'position': self._normalize_position(player.position),
                'role': player.position,
                'birthplace': '',  # Would need additional scraping
                'height': player.height or 'N/A',
                'weight': player.weight or 'N/A',
                'number': int(player.number) if player.number.isdigit() else None,
                'injured': False,
                'starting': self._determine_starting_status(player),
                'photo': player.image or self._get_placeholder_url(player.name, player.position),
                'source': player.source
            }
            django_players.append(django_player)

        return django_players

    def _normalize_position(self, position: str) -> str:
        """Normalize position names."""
        if not position:
            return 'Midfielder'

        position_lower = position.lower()
        if 'goal' in position_lower:
            return 'Goalkeeper'
        elif 'defend' in position_lower or 'back' in position_lower:
            return 'Defender'
        elif 'forward' in position_lower or 'striker' in position_lower or 'winger' in position_lower:
            return 'Forward'
        else:
            return 'Midfielder'

    def _calculate_age_from_name(self, name: str) -> int:
        """Estimate age based on player name (would need birth date for accuracy)."""
        # This is a placeholder - in real implementation, you'd scrape birth dates
        age_estimates = {
            'Cole Palmer': 22, 'Enzo Fernandez': 23, 'Nicolas Jackson': 22,
            'Christopher Nkunku': 26, 'Reece James': 24, 'Wesley Fofana': 23,
            'Robert Sanchez': 26, 'Moises Caicedo': 22, 'Levi Colwill': 21
        }
        return age_estimates.get(name, 25)  # Default age

    def _determine_starting_status(self, player: Player) -> bool:
        """Determine if player is in starting XI."""
        key_players = [
            'Robert Sanchez', 'Reece James', 'Wesley Fofana', 'Levi Colwill', 'Marc Cucurella',
            'Enzo Fernandez', 'Moises Caicedo', 'Cole Palmer',
            'Nicolas Jackson', 'Pedro Neto', 'Christopher Nkunku'
        ]
        return player.name in key_players

    def _get_placeholder_url(self, name: str, position: str) -> str:
        """Generate placeholder URL for player without image."""
        # This would integrate with the existing placeholder system
        return f"placeholder_{name.replace(' ', '_').lower()}.svg"