"""
Resume and Cover Letter Generator
Generates tailored resumes and cover letters based on user profile and job description
"""

from typing import Dict, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import os
from datetime import datetime

# ============================================================================
# RESUME GENERATOR
# ============================================================================

class ResumeGenerator:
    """
    Generates tailored resumes based on user profile and job requirements.
    """
    
    def __init__(self, llm_model: str = "claude-sonnet-4-20250514"):
        self.llm = ChatAnthropic(
            model=llm_model,
            temperature=0.3,  # Slightly creative but consistent
            max_tokens=4096
        )
    
    def generate_resume(
        self,
        user_profile: Dict,
        job_description: str,
        format: str = "professional"
    ) -> str:
        """
        Generate a tailored resume for a specific job.
        
        Args:
            user_profile: User's LinkedIn profile data
            job_description: Target job description
            format: Resume format (professional, creative, technical, ats)
            
        Returns:
            Formatted resume text
        """
        system_prompt = """You are an expert resume writer and career coach. Your task is to create a compelling, 
ATS-friendly resume tailored to the specific job description while highlighting the candidate's relevant experience.

Guidelines:
1. Use the user's actual experience and skills - never fabricate
2. Emphasize relevant experience that matches job requirements
3. Use strong action verbs and quantifiable achievements
4. Keep it concise - aim for 1-2 pages
5. Optimize for ATS (Applicant Tracking Systems) with relevant keywords
6. Format clearly with proper sections
7. Highlight transferable skills if changing careers

Sections to include:
- Contact Information
- Professional Summary (3-4 lines)
- Work Experience (most recent 3-5 positions)
- Education
- Skills (categorized if many)
- Certifications (if relevant)
- Optional: Projects, Languages, Volunteer Work

Return the resume in clean, professional text format."""

        user_prompt = f"""Create a tailored resume for this candidate:

**CANDIDATE PROFILE:**
Name: {user_profile.get('name', 'Candidate')}
Location: {user_profile.get('location', 'Not specified')}
Headline: {user_profile.get('headline', '')}

About:
{user_profile.get('about', 'Not provided')}

Work Experience:
{self._format_experience(user_profile.get('experience', []))}

Education:
{self._format_education(user_profile.get('education', []))}

Skills:
{', '.join(user_profile.get('skills', [])[:30])}

Certifications:
{self._format_certifications(user_profile.get('certifications', []))}

Languages:
{', '.join(user_profile.get('languages', []))}

---

**TARGET JOB DESCRIPTION:**
{job_description}

---

**RESUME FORMAT:** {format}

Create a compelling resume that:
1. Highlights experience relevant to this specific job
2. Uses keywords from the job description naturally
3. Emphasizes quantifiable achievements
4. Shows clear career progression
5. Demonstrates the candidate is a strong match

Generate the complete resume now:"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_resume_multiple_formats(
        self,
        user_profile: Dict,
        job_description: str
    ) -> Dict[str, str]:
        """
        Generate resume in multiple formats.
        
        Returns:
            Dictionary with different format versions
        """
        formats = {
            'professional': self.generate_resume(user_profile, job_description, 'professional'),
            'ats_optimized': self.generate_resume(user_profile, job_description, 'ats'),
            'technical': self.generate_resume(user_profile, job_description, 'technical'),
        }
        return formats
    
    def _format_experience(self, experiences: list) -> str:
        """Format experience for prompt"""
        if not experiences:
            return "No experience provided"
        
        formatted = []
        for exp in experiences[:5]:  # Top 5
            entry = f"- {exp.get('title', 'Position')} at {exp.get('company', 'Company')}"
            if exp.get('duration'):
                entry += f" ({exp.get('duration')})"
            if exp.get('description'):
                entry += f"\n  {exp.get('description')}"
            formatted.append(entry)
        
        return "\n".join(formatted)
    
    def _format_education(self, education: list) -> str:
        """Format education for prompt"""
        if not education:
            return "No education provided"
        
        formatted = []
        for edu in education:
            entry = f"- {edu.get('degree', 'Degree')} from {edu.get('school', 'Institution')}"
            if edu.get('field'):
                entry += f" in {edu.get('field')}"
            if edu.get('years'):
                entry += f" ({edu.get('years')})"
            formatted.append(entry)
        
        return "\n".join(formatted)
    
    def _format_certifications(self, certifications: list) -> str:
        """Format certifications for prompt"""
        if not certifications:
            return "None"
        
        formatted = []
        for cert in certifications:
            entry = f"- {cert.get('name', 'Certification')}"
            if cert.get('issuer'):
                entry += f" by {cert.get('issuer')}"
            formatted.append(entry)
        
        return "\n".join(formatted)


# ============================================================================
# COVER LETTER GENERATOR
# ============================================================================

class CoverLetterGenerator:
    """
    Generates personalized cover letters based on user profile and job.
    """
    
    def __init__(self, llm_model: str = "claude-sonnet-4-20250514"):
        self.llm = ChatAnthropic(
            model=llm_model,
            temperature=0.4,  # More creative for cover letters
            max_tokens=2048
        )
    
    def generate_cover_letter(
        self,
        user_profile: Dict,
        job_title: str,
        company_name: str,
        job_description: str,
        tone: str = "professional"
    ) -> str:
        """
        Generate a personalized cover letter.
        
        Args:
            user_profile: User's LinkedIn profile data
            job_title: Job title
            company_name: Company name
            job_description: Full job description
            tone: professional, enthusiastic, formal, creative
            
        Returns:
            Formatted cover letter
        """
        system_prompt = """You are an expert cover letter writer. Your task is to create compelling, 
personalized cover letters that stand out while maintaining professionalism.

Guidelines:
1. Start with a strong opening that grabs attention
2. Show genuine enthusiasm for the specific role and company
3. Highlight 2-3 key achievements relevant to the job
4. Demonstrate understanding of the company and role
5. Show personality while staying professional
6. Keep it concise - aim for 3-4 paragraphs, max 400 words
7. End with a clear call to action
8. Use the candidate's actual experience - never fabricate
9. Avoid clichés like "I am writing to apply" or "I am a hard worker"

Structure:
- Opening: Hook that shows enthusiasm and relevance
- Body 1: Why you're interested in this specific role/company
- Body 2: Your relevant experience and achievements
- Closing: Call to action and appreciation

Make it engaging, authentic, and memorable."""

        user_prompt = f"""Create a compelling cover letter for this application:

**CANDIDATE:**
Name: {user_profile.get('name', 'Candidate')}
Current Role: {user_profile.get('headline', 'Professional')}
Location: {user_profile.get('location', 'Not specified')}

About:
{user_profile.get('about', 'Not provided')[:500]}

Key Experience:
{self._get_relevant_experience(user_profile.get('experience', []), job_description)}

Skills:
{', '.join(user_profile.get('skills', [])[:15])}

---

**TARGET POSITION:**
Job Title: {job_title}
Company: {company_name}

Job Description:
{job_description[:1500]}

---

**TONE:** {tone}

Create a compelling cover letter that:
1. Opens with genuine enthusiasm for this specific role
2. Demonstrates understanding of {company_name} and what they do
3. Highlights 2-3 specific achievements that match job requirements
4. Shows why this candidate is uniquely qualified
5. Ends with a strong call to action
6. Sounds authentic and personal, not generic

Generate the complete cover letter now:"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_cover_letter_variations(
        self,
        user_profile: Dict,
        job_title: str,
        company_name: str,
        job_description: str
    ) -> Dict[str, str]:
        """
        Generate cover letter in different tones.
        
        Returns:
            Dictionary with different tone variations
        """
        tones = {
            'professional': self.generate_cover_letter(
                user_profile, job_title, company_name, job_description, 'professional'
            ),
            'enthusiastic': self.generate_cover_letter(
                user_profile, job_title, company_name, job_description, 'enthusiastic'
            ),
            'concise': self.generate_cover_letter(
                user_profile, job_title, company_name, job_description, 'concise'
            ),
        }
        return tones
    
    def _get_relevant_experience(self, experiences: list, job_description: str) -> str:
        """Extract most relevant experience based on job description"""
        if not experiences:
            return "No experience provided"
        
        # For now, just return top 3
        # In production, could use similarity matching
        formatted = []
        for exp in experiences[:3]:
            entry = f"- {exp.get('title', 'Position')} at {exp.get('company', 'Company')}"
            if exp.get('duration'):
                entry += f" ({exp.get('duration')})"
            if exp.get('description'):
                entry += f"\n  {exp.get('description')[:200]}"
            formatted.append(entry)
        
        return "\n".join(formatted)


# ============================================================================
# COMBINED APPLICATION PACKAGE GENERATOR
# ============================================================================

class ApplicationPackageGenerator:
    """
    Generates complete application package: resume + cover letter.
    """
    
    def __init__(self):
        self.resume_gen = ResumeGenerator()
        self.cover_gen = CoverLetterGenerator()
    
    def generate_application_package(
        self,
        user_profile: Dict,
        job_title: str,
        company_name: str,
        job_description: str,
        include_variations: bool = False
    ) -> Dict:
        """
        Generate complete application package.
        
        Args:
            user_profile: User's profile data
            job_title: Target job title
            company_name: Target company
            job_description: Full job description
            include_variations: Whether to include multiple format variations
            
        Returns:
            Dictionary containing resume and cover letter
        """
        package = {
            'generated_at': datetime.now().isoformat(),
            'job_title': job_title,
            'company': company_name,
            'candidate': user_profile.get('name', 'Candidate'),
        }
        
        if include_variations:
            package['resumes'] = self.resume_gen.generate_resume_multiple_formats(
                user_profile, job_description
            )
            package['cover_letters'] = self.cover_gen.generate_cover_letter_variations(
                user_profile, job_title, company_name, job_description
            )
        else:
            package['resume'] = self.resume_gen.generate_resume(
                user_profile, job_description
            )
            package['cover_letter'] = self.cover_gen.generate_cover_letter(
                user_profile, job_title, company_name, job_description
            )
        
        return package
    
    def save_package_to_files(
        self,
        package: Dict,
        output_dir: str = "application_materials"
    ) -> Dict[str, str]:
        """
        Save application package to files.
        
        Returns:
            Dictionary with file paths
        """
        import os
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename base
        company = package['company'].replace(' ', '_')
        job = package['job_title'].replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{company}_{job}_{timestamp}"
        
        files = {}
        
        # Save resume
        if 'resume' in package:
            resume_path = os.path.join(output_dir, f"{base_name}_resume.txt")
            with open(resume_path, 'w') as f:
                f.write(package['resume'])
            files['resume'] = resume_path
        
        # Save cover letter
        if 'cover_letter' in package:
            cover_path = os.path.join(output_dir, f"{base_name}_cover_letter.txt")
            with open(cover_path, 'w') as f:
                f.write(package['cover_letter'])
            files['cover_letter'] = cover_path
        
        # Save variations if present
        if 'resumes' in package:
            for format_name, content in package['resumes'].items():
                path = os.path.join(output_dir, f"{base_name}_resume_{format_name}.txt")
                with open(path, 'w') as f:
                    f.write(content)
                files[f'resume_{format_name}'] = path
        
        if 'cover_letters' in package:
            for tone_name, content in package['cover_letters'].items():
                path = os.path.join(output_dir, f"{base_name}_cover_{tone_name}.txt")
                with open(path, 'w') as f:
                    f.write(content)
                files[f'cover_{tone_name}'] = path
        
        return files


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_resume_for_job(
    user_profile: Dict,
    job_description: str,
    format: str = "professional"
) -> str:
    """Quick function to generate resume"""
    generator = ResumeGenerator()
    return generator.generate_resume(user_profile, job_description, format)


def generate_cover_letter_for_job(
    user_profile: Dict,
    job_title: str,
    company_name: str,
    job_description: str,
    tone: str = "professional"
) -> str:
    """Quick function to generate cover letter"""
    generator = CoverLetterGenerator()
    return generator.generate_cover_letter(
        user_profile, job_title, company_name, job_description, tone
    )


def generate_full_application(
    user_profile: Dict,
    job_title: str,
    company_name: str,
    job_description: str,
    save_to_files: bool = True
) -> Dict:
    """Quick function to generate full application package"""
    generator = ApplicationPackageGenerator()
    package = generator.generate_application_package(
        user_profile, job_title, company_name, job_description
    )
    
    if save_to_files:
        files = generator.save_package_to_files(package)
        package['saved_files'] = files
    
    return package


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Resume & Cover Letter Generator - Test Mode")
    print("=" * 60)
    
    # Mock user profile for testing
    mock_profile = {
        'name': 'John Doe',
        'location': 'San Francisco, CA',
        'headline': 'Senior Software Engineer | AI/ML Enthusiast',
        'about': 'Experienced software engineer with 5+ years in building scalable systems and ML applications.',
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp',
                'duration': '2020 - Present',
                'description': 'Led development of ML-powered recommendation system serving 10M+ users.'
            },
            {
                'title': 'Software Engineer',
                'company': 'StartupXYZ',
                'duration': '2018 - 2020',
                'description': 'Built microservices architecture handling 1M+ daily requests.'
            }
        ],
        'education': [
            {
                'school': 'University of California',
                'degree': 'BS Computer Science',
                'field': 'Computer Science',
                'years': '2014 - 2018'
            }
        ],
        'skills': ['Python', 'Machine Learning', 'AWS', 'Docker', 'Kubernetes', 'TensorFlow'],
        'certifications': [
            {'name': 'AWS Solutions Architect', 'issuer': 'Amazon'},
        ],
        'languages': ['English', 'Spanish']
    }
    
    mock_job_description = """
    Senior ML Engineer
    
    We're seeking an experienced ML engineer to join our team and build next-generation AI systems.
    
    Requirements:
    - 5+ years of software engineering experience
    - 2+ years of ML/AI experience
    - Strong Python skills
    - Experience with TensorFlow or PyTorch
    - Cloud platform experience (AWS/GCP)
    
    Responsibilities:
    - Design and implement ML models
    - Build scalable ML pipelines
    - Collaborate with cross-functional teams
    """
    
    print("\n[Generating Application Package]")
    print("-" * 60)
    
    generator = ApplicationPackageGenerator()
    package = generator.generate_application_package(
        user_profile=mock_profile,
        job_title="Senior ML Engineer",
        company_name="AI Innovations Inc",
        job_description=mock_job_description
    )
    
    print("\n✅ Application package generated!")
    print("\n[RESUME]")
    print("=" * 60)
    print(package['resume'][:500] + "...\n")
    
    print("[COVER LETTER]")
    print("=" * 60)
    print(package['cover_letter'][:500] + "...\n")
    
    # Save to files
    print("[Saving to files...]")
    files = generator.save_package_to_files(package)
    print(f"✅ Saved {len(files)} files:")
    for file_type, path in files.items():
        print(f"  - {file_type}: {path}")
    
    print("\n" + "=" * 60)
    print("Test complete!")