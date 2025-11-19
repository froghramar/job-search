"""
LinkedIn Profile Fetcher
Fetches user profile data from LinkedIn in real-time
"""

import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re

# ============================================================================
# METHOD 1: Public Profile Scraper (No Authentication)
# ============================================================================

class LinkedInProfileScraper:
    """
    Scrapes public LinkedIn profile without authentication.
    Works with public profile URLs.
    """
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com/in/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_profile(self, handle: str) -> Optional[Dict]:
        """
        Fetch LinkedIn profile data from public profile.
        
        Args:
            handle: LinkedIn username (e.g., 'john-doe')
            
        Returns:
            Dictionary containing profile information
        """
        url = f"{self.base_url}{handle}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract profile data from public page
            profile = {
                'handle': handle,
                'url': url,
                'name': self._extract_name(soup),
                'headline': self._extract_headline(soup),
                'location': self._extract_location(soup),
                'about': self._extract_about(soup),
                'experience': self._extract_experience(soup),
                'education': self._extract_education(soup),
                'skills': self._extract_skills(soup),
                'languages': self._extract_languages(soup),
                'certifications': self._extract_certifications(soup),
            }
            
            return profile
            
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None
    
    def _extract_name(self, soup) -> str:
        """Extract full name"""
        name_elem = soup.find('h1', class_='top-card-layout__title')
        if name_elem:
            return name_elem.get_text(strip=True)
        
        # Try alternative selector
        name_elem = soup.find('h1', {'class': re.compile(r'.*name.*', re.I)})
        return name_elem.get_text(strip=True) if name_elem else "Not found"
    
    def _extract_headline(self, soup) -> str:
        """Extract professional headline"""
        headline_elem = soup.find('h2', class_='top-card-layout__headline')
        if headline_elem:
            return headline_elem.get_text(strip=True)
        
        # Try alternative
        headline_elem = soup.find('div', {'class': re.compile(r'.*headline.*', re.I)})
        return headline_elem.get_text(strip=True) if headline_elem else "Not found"
    
    def _extract_location(self, soup) -> str:
        """Extract location"""
        location_elem = soup.find('div', class_='top-card__subline-item')
        return location_elem.get_text(strip=True) if location_elem else "Not specified"
    
    def _extract_about(self, soup) -> str:
        """Extract about/summary section"""
        about_section = soup.find('section', {'class': re.compile(r'.*about.*', re.I)})
        if about_section:
            about_text = about_section.find('div', {'class': re.compile(r'.*inline-show-more-text.*', re.I)})
            if about_text:
                return about_text.get_text(strip=True)
        return ""
    
    def _extract_experience(self, soup) -> List[Dict]:
        """Extract work experience"""
        experiences = []
        
        exp_section = soup.find('section', {'id': re.compile(r'.*experience.*', re.I)})
        if exp_section:
            exp_items = exp_section.find_all('li', class_='profile-section-card')
            
            for item in exp_items[:5]:  # Limit to 5 most recent
                try:
                    title_elem = item.find('h3')
                    company_elem = item.find('h4')
                    duration_elem = item.find('span', {'class': re.compile(r'.*date-range.*', re.I)})
                    
                    experience = {
                        'title': title_elem.get_text(strip=True) if title_elem else '',
                        'company': company_elem.get_text(strip=True) if company_elem else '',
                        'duration': duration_elem.get_text(strip=True) if duration_elem else '',
                        'description': ''
                    }
                    
                    if experience['title'] or experience['company']:
                        experiences.append(experience)
                except:
                    continue
        
        return experiences
    
    def _extract_education(self, soup) -> List[Dict]:
        """Extract education history"""
        education = []
        
        edu_section = soup.find('section', {'id': re.compile(r'.*education.*', re.I)})
        if edu_section:
            edu_items = edu_section.find_all('li', class_='profile-section-card')
            
            for item in edu_items[:3]:  # Limit to 3
                try:
                    school_elem = item.find('h3')
                    degree_elem = item.find('h4')
                    
                    edu_entry = {
                        'school': school_elem.get_text(strip=True) if school_elem else '',
                        'degree': degree_elem.get_text(strip=True) if degree_elem else '',
                    }
                    
                    if edu_entry['school']:
                        education.append(edu_entry)
                except:
                    continue
        
        return education
    
    def _extract_skills(self, soup) -> List[str]:
        """Extract skills"""
        skills = []
        
        skills_section = soup.find('section', {'id': re.compile(r'.*skills.*', re.I)})
        if skills_section:
            skill_items = skills_section.find_all('span', {'class': re.compile(r'.*skill.*', re.I)})
            
            for item in skill_items[:20]:  # Limit to top 20
                skill_text = item.get_text(strip=True)
                if skill_text and len(skill_text) < 50:  # Filter out long text
                    skills.append(skill_text)
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_languages(self, soup) -> List[str]:
        """Extract languages"""
        languages = []
        
        lang_section = soup.find('section', {'id': re.compile(r'.*languages.*', re.I)})
        if lang_section:
            lang_items = lang_section.find_all('li')
            
            for item in lang_items:
                lang_text = item.get_text(strip=True)
                if lang_text:
                    languages.append(lang_text)
        
        return languages
    
    def _extract_certifications(self, soup) -> List[Dict]:
        """Extract certifications"""
        certifications = []
        
        cert_section = soup.find('section', {'id': re.compile(r'.*certifications.*', re.I)})
        if cert_section:
            cert_items = cert_section.find_all('li', class_='profile-section-card')
            
            for item in cert_items[:5]:
                try:
                    name_elem = item.find('h3')
                    issuer_elem = item.find('h4')
                    
                    cert = {
                        'name': name_elem.get_text(strip=True) if name_elem else '',
                        'issuer': issuer_elem.get_text(strip=True) if issuer_elem else '',
                    }
                    
                    if cert['name']:
                        certifications.append(cert)
                except:
                    continue
        
        return certifications


# ============================================================================
# METHOD 2: LinkedIn API Client (Authenticated)
# ============================================================================

class LinkedInAPIProfileClient:
    """
    Uses linkedin-api library for authenticated profile access.
    Provides more complete data but requires LinkedIn credentials.
    """
    
    def __init__(self, email: str = None, password: str = None):
        try:
            from linkedin_api import Linkedin
            
            email = email or os.getenv('LINKEDIN_EMAIL')
            password = password or os.getenv('LINKEDIN_PASSWORD')
            
            if not email or not password:
                raise ValueError("LinkedIn credentials required. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD.")
            
            self.api = Linkedin(email, password)
            
        except ImportError:
            print("linkedin-api not installed. Install with: pip install linkedin-api")
            raise
    
    def get_profile(self, handle: str) -> Optional[Dict]:
        """
        Fetch profile using LinkedIn API.
        
        Args:
            handle: LinkedIn username
            
        Returns:
            Dictionary containing comprehensive profile data
        """
        try:
            # Get profile data
            profile = self.api.get_profile(handle)
            
            # Format the data
            formatted_profile = {
                'handle': handle,
                'url': f"https://www.linkedin.com/in/{handle}",
                'name': f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
                'headline': profile.get('headline', ''),
                'location': self._format_location(profile.get('geoLocation', {})),
                'about': profile.get('summary', ''),
                'experience': self._format_experience(profile.get('experience', [])),
                'education': self._format_education(profile.get('education', [])),
                'skills': self._format_skills(profile.get('skills', [])),
                'languages': self._format_languages(profile.get('languages', [])),
                'certifications': self._format_certifications(profile.get('certifications', [])),
                'volunteer': self._format_volunteer(profile.get('volunteer', [])),
                'projects': self._format_projects(profile.get('projects', [])),
            }
            
            return formatted_profile
            
        except Exception as e:
            print(f"Error fetching profile via API: {e}")
            return None
    
    def _format_location(self, geo_data: Dict) -> str:
        """Format location data"""
        if geo_data:
            return f"{geo_data.get('city', '')}, {geo_data.get('country', '')}".strip(', ')
        return "Not specified"
    
    def _format_experience(self, experiences: List) -> List[Dict]:
        """Format experience data"""
        formatted = []
        for exp in experiences[:10]:  # Limit to 10
            formatted.append({
                'title': exp.get('title', ''),
                'company': exp.get('companyName', ''),
                'duration': f"{exp.get('timePeriod', {}).get('startDate', {})} - {exp.get('timePeriod', {}).get('endDate', {}) or 'Present'}",
                'description': exp.get('description', ''),
                'location': exp.get('locationName', '')
            })
        return formatted
    
    def _format_education(self, education: List) -> List[Dict]:
        """Format education data"""
        formatted = []
        for edu in education:
            formatted.append({
                'school': edu.get('schoolName', ''),
                'degree': edu.get('degreeName', ''),
                'field': edu.get('fieldOfStudy', ''),
                'years': f"{edu.get('timePeriod', {}).get('startDate', {})} - {edu.get('timePeriod', {}).get('endDate', {})}"
            })
        return formatted
    
    def _format_skills(self, skills: List) -> List[str]:
        """Format skills data"""
        return [skill.get('name', '') for skill in skills if skill.get('name')]
    
    def _format_languages(self, languages: List) -> List[str]:
        """Format languages data"""
        return [lang.get('name', '') for lang in languages if lang.get('name')]
    
    def _format_certifications(self, certs: List) -> List[Dict]:
        """Format certifications data"""
        formatted = []
        for cert in certs:
            formatted.append({
                'name': cert.get('name', ''),
                'issuer': cert.get('authority', ''),
                'date': cert.get('timePeriod', {}).get('startDate', {})
            })
        return formatted
    
    def _format_volunteer(self, volunteer: List) -> List[Dict]:
        """Format volunteer experience"""
        formatted = []
        for vol in volunteer:
            formatted.append({
                'role': vol.get('role', ''),
                'organization': vol.get('companyName', ''),
                'cause': vol.get('cause', '')
            })
        return formatted
    
    def _format_projects(self, projects: List) -> List[Dict]:
        """Format projects"""
        formatted = []
        for proj in projects:
            formatted.append({
                'title': proj.get('title', ''),
                'description': proj.get('description', ''),
                'url': proj.get('url', '')
            })
        return formatted


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def get_profile_fetcher(method: str = "auto"):
    """
    Factory function to get the best available profile fetcher.
    
    Args:
        method: "auto", "public", or "api"
        
    Returns:
        Profile fetcher instance
    """
    if method == "api":
        return LinkedInAPIProfileClient()
    elif method == "public":
        return LinkedInProfileScraper()
    else:  # auto
        try:
            return LinkedInAPIProfileClient()
        except:
            return LinkedInProfileScraper()


def get_user_profile(handle: str = None) -> Optional[Dict]:
    """
    Convenience function to get user profile.
    Automatically tries best available method.
    
    Args:
        handle: LinkedIn username (defaults to env variable)
        
    Returns:
        Profile dictionary
    """
    handle = handle or os.getenv('LINKEDIN_USER_HANDLE')
    
    if not handle:
        print("No LinkedIn handle provided. Set LINKEDIN_USER_HANDLE in .env")
        return None
    
    try:
        fetcher = get_profile_fetcher()
        return fetcher.get_profile(handle)
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return None


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("LinkedIn Profile Fetcher - Test Mode")
    print("=" * 60)
    
    # Get handle from command line or env
    handle = sys.argv[1] if len(sys.argv) > 1 else os.getenv('LINKEDIN_USER_HANDLE')
    
    if not handle:
        print("Usage: python profile_fetcher.py <linkedin-handle>")
        print("Or set LINKEDIN_USER_HANDLE in .env")
        sys.exit(1)
    
    print(f"\nFetching profile for: {handle}")
    print("-" * 60)
    
    # Try public scraper first
    print("\n[Method 1: Public Scraper]")
    scraper = LinkedInProfileScraper()
    profile = scraper.get_profile(handle)
    
    if profile:
        print(f"\n✅ Profile fetched successfully!")
        print(f"Name: {profile['name']}")
        print(f"Headline: {profile['headline']}")
        print(f"Location: {profile['location']}")
        print(f"Skills: {', '.join(profile['skills'][:5])}")
        print(f"Experience entries: {len(profile['experience'])}")
        print(f"Education entries: {len(profile['education'])}")
        
        # Print full profile as JSON
        print("\n" + "=" * 60)
        print("Full Profile Data:")
        print(json.dumps(profile, indent=2))
    else:
        print("❌ Failed to fetch profile")
    
    print("\n" + "=" * 60)
    print("Test complete!")