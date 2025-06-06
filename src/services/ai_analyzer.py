"""
Enhanced AI Analyzer service with multiple AI providers support
"""
import asyncio
import aiohttp
import json
import random
import os
from typing import Dict, Optional, List
from datetime import datetime

class AIAnalyzer:
    def __init__(self):
        # Multiple AI service endpoints
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        
        # API keys from environment
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Fallback to simulation if no keys provided
        self.use_simulation = not (self.openai_key or self.anthropic_key)
        
        # Domain categories
        self.categories = [
            "E-commerce", "Technology", "News & Media", "Education", 
            "Healthcare", "Finance", "Entertainment", "Travel",
            "Food & Beverage", "Fashion", "Real Estate", "Sports",
            "Gaming", "Social Media", "Business Services", "Automotive",
            "Legal", "Non-profit", "Government", "Personal Blog", "Other"
        ]
        
        # Enhanced keyword mapping
        self.keyword_mapping = {
            "E-commerce": [
                "shop", "store", "buy", "sell", "market", "cart", "checkout", 
                "retail", "commerce", "mall", "bazaar", "outlet", "deals"
            ],
            "Technology": [
                "tech", "soft", "dev", "code", "app", "digital", "cyber", 
                "data", "cloud", "ai", "ml", "blockchain", "crypto", "api"
            ],
            "News & Media": [
                "news", "media", "blog", "post", "journal", "press", "times",
                "herald", "gazette", "daily", "weekly", "magazine", "radio"
            ],
            "Education": [
                "edu", "learn", "course", "school", "university", "college",
                "academy", "training", "tutorial", "study", "class", "lesson"
            ],
            "Healthcare": [
                "health", "medical", "doctor", "clinic", "hospital", "care",
                "wellness", "fitness", "pharmacy", "dental", "therapy"
            ],
            "Finance": [
                "bank", "finance", "money", "invest", "loan", "credit", "pay",
                "wallet", "fund", "capital", "trading", "forex", "crypto"
            ],
            "Gaming": [
                "game", "play", "gaming", "esport", "gamer", "arcade", "console",
                "steam", "xbox", "playstation", "nintendo", "mmo", "rpg"
            ],
            "Travel": [
                "travel", "hotel", "flight", "tour", "trip", "vacation", "booking",
                "airline", "resort", "cruise", "adventure", "explore"
            ],
            "Food & Beverage": [
                "food", "restaurant", "recipe", "cook", "cafe", "bar", "pizza",
                "delivery", "catering", "dining", "kitchen", "chef", "menu"
            ],
            "Fashion": [
                "fashion", "cloth", "style", "beauty", "dress", "wear", "boutique",
                "designer", "trend", "makeup", "cosmetic", "jewelry"
            ],
            "Real Estate": [
                "real", "estate", "property", "rent", "house", "home", "apartment",
                "realty", "mortgage", "construction", "architecture"
            ],
            "Sports": [
                "sport", "team", "athlete", "fitness", "gym", "football", "soccer",
                "basketball", "tennis", "golf", "running", "marathon"
            ],
            "Social Media": [
                "social", "chat", "connect", "network", "community", "forum",
                "messenger", "dating", "friend", "share", "post", "like"
            ],
            "Automotive": [
                "car", "auto", "vehicle", "motor", "drive", "garage", "repair",
                "parts", "dealer", "racing", "truck", "motorcycle"
            ],
            "Legal": [
                "law", "legal", "lawyer", "attorney", "court", "justice", "firm",
                "advocate", "counsel", "litigation", "patent", "trademark"
            ],
            "Non-profit": [
                "charity", "foundation", "nonprofit", "donation", "volunteer",
                "cause", "help", "support", "community", "welfare"
            ],
            "Government": [
                "gov", "government", "official", "public", "municipal", "federal",
                "state", "city", "county", "agency", "department"
            ],
            "Personal Blog": [
                "personal", "blog", "diary", "journal", "life", "story", "thoughts",
                "experience", "portfolio", "resume", "cv", "about"
            ]
        }
        
    async def analyze_domain_theme(self, domain: str, use_ai: bool = True) -> Dict:
        """Analyze domain theme using AI or simulation"""
        try:
            if use_ai and not self.use_simulation:
                # Try real AI analysis first
                result = await self._try_ai_providers(domain)
                if result:
                    return result
            
            # Fallback to enhanced simulation
            return await self._enhanced_simulation_analysis(domain)
            
        except Exception as e:
            print(f"Error in AI analysis for {domain}: {str(e)}")
            return self._get_default_ai_result()
    
    async def _try_ai_providers(self, domain: str) -> Optional[Dict]:
        """Try different AI providers in order of preference"""
        
        # Try OpenAI first
        if self.openai_key:
            try:
                result = await self._call_openai_api(domain)
                if result and result.get('ai_confidence', 0) > 0.3:
                    return result
            except Exception as e:
                print(f"OpenAI API failed: {str(e)}")
        
        # Try Anthropic as fallback
        if self.anthropic_key:
            try:
                result = await self._call_anthropic_api(domain)
                if result and result.get('ai_confidence', 0) > 0.3:
                    return result
            except Exception as e:
                print(f"Anthropic API failed: {str(e)}")
        
        return None
    
    async def _enhanced_simulation_analysis(self, domain: str) -> Dict:
        """Enhanced simulation with better categorization logic"""
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.3, 1.5))
        
        domain_lower = domain.lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in self.keyword_mapping.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in domain_lower:
                    score += 1
                    matched_keywords.append(keyword)
                    
                    # Bonus for exact matches or word boundaries
                    if f".{keyword}." in f".{domain_lower}.":
                        score += 0.5
            
            if score > 0:
                category_scores[category] = {
                    'score': score,
                    'keywords': matched_keywords
                }
        
        # Determine best category
        if category_scores:
            best_category = max(category_scores.keys(), 
                              key=lambda x: category_scores[x]['score'])
            confidence = min(0.9, 0.4 + (category_scores[best_category]['score'] * 0.2))
            matched_keywords = category_scores[best_category]['keywords']
        else:
            # Fallback analysis based on TLD and common patterns
            best_category, confidence, matched_keywords = self._analyze_by_patterns(domain_lower)
        
        # Generate themes based on category
        themes = self._generate_themes(best_category, matched_keywords)
        
        # Create description
        description = self._generate_description(domain, best_category, themes, confidence)
        
        # Determine if domain is recommended
        recommended = self._is_domain_recommended(best_category, confidence, domain)
        
        analysis_result = {
            "category": best_category,
            "themes": themes,
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "analysis_method": "enhanced_pattern_matching",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "recommended": recommended
        }
        
        return {
            "thematic_analysis_result": json.dumps(analysis_result),
            "ai_category": best_category,
            "ai_confidence": confidence,
            "ai_description": description,
            "recommended": recommended
        }
    
    def _analyze_by_patterns(self, domain_lower: str) -> tuple:
        """Analyze domain by TLD and common patterns"""
        
        # TLD-based analysis
        if domain_lower.endswith('.edu'):
            return "Education", 0.8, ["educational institution"]
        elif domain_lower.endswith('.gov'):
            return "Government", 0.9, ["government"]
        elif domain_lower.endswith('.org'):
            return "Non-profit", 0.6, ["organization"]
        elif domain_lower.endswith('.mil'):
            return "Government", 0.9, ["military"]
        
        # Length-based heuristics
        if len(domain_lower.split('.')[0]) <= 4:
            return "Technology", 0.4, ["short domain"]
        
        # Number patterns
        if any(char.isdigit() for char in domain_lower):
            return "Technology", 0.3, ["contains numbers"]
        
        # Default fallback
        return "Other", 0.2, ["unknown pattern"]
    
    def _generate_themes(self, category: str, matched_keywords: List[str]) -> List[str]:
        """Generate relevant themes for the category"""
        
        theme_map = {
            "E-commerce": ["online retail", "marketplace", "shopping"],
            "Technology": ["software development", "digital solutions", "innovation"],
            "News & Media": ["journalism", "content publishing", "information"],
            "Education": ["learning platform", "educational content", "knowledge sharing"],
            "Healthcare": ["medical services", "wellness", "health information"],
            "Finance": ["financial services", "investment", "banking"],
            "Gaming": ["video games", "entertainment", "interactive media"],
            "Travel": ["tourism", "hospitality", "travel services"],
            "Food & Beverage": ["culinary", "dining", "food services"],
            "Fashion": ["style", "apparel", "beauty"],
            "Real Estate": ["property services", "real estate", "housing"],
            "Sports": ["athletics", "fitness", "sports content"],
            "Social Media": ["social networking", "community", "communication"],
            "Automotive": ["automotive services", "vehicles", "transportation"],
            "Legal": ["legal services", "law practice", "legal information"],
            "Non-profit": ["charitable organization", "social cause", "community service"],
            "Government": ["public service", "government information", "civic"],
            "Personal Blog": ["personal content", "blogging", "individual expression"],
            "Other": ["general purpose", "miscellaneous", "unspecified"]
        }
        
        base_themes = theme_map.get(category, ["general"])
        
        # Add matched keywords as themes if relevant
        if matched_keywords:
            combined_themes = base_themes + matched_keywords[:2]
            return list(set(combined_themes))[:3]  # Limit to 3 themes
        
        return base_themes[:2]
    
    def _generate_description(self, domain: str, category: str, themes: List[str], confidence: float) -> str:
        """Generate human-readable description"""
        
        confidence_text = "high" if confidence > 0.7 else "moderate" if confidence > 0.4 else "low"
        
        description = f"Domain '{domain}' is categorized as {category} with {confidence_text} confidence ({confidence:.1%}). "
        
        if themes:
            description += f"Key themes include: {', '.join(themes)}. "
        
        if confidence > 0.6:
            description += "This categorization is based on strong domain name indicators."
        elif confidence > 0.3:
            description += "This categorization is based on partial domain name analysis."
        else:
            description += "This categorization is tentative due to limited domain name indicators."
        
        return description
    
    def _is_domain_recommended(self, category: str, confidence: float, domain: str) -> bool:
        """Determine if domain should be recommended"""
        
        # High-value categories
        high_value_categories = [
            "E-commerce", "Technology", "Finance", "Healthcare", 
            "Education", "Real Estate", "Legal"
        ]
        
        # Recommendation logic
        if category in high_value_categories and confidence > 0.6:
            return True
        
        if confidence > 0.8:  # Very high confidence regardless of category
            return True
        
        # Domain quality indicators
        domain_name = domain.split('.')[0].lower()
        if len(domain_name) <= 8 and domain_name.isalpha():  # Short, clean domains
            return True
        
        return False
    
    async def _call_openai_api(self, domain: str) -> Dict:
        """Call OpenAI API for actual AI analysis"""
        
        prompt = f"""
        Analyze the domain name "{domain}" and provide a comprehensive thematic categorization.
        
        Consider:
        1. The domain name structure and keywords
        2. Common web industry patterns
        3. Likely business purpose and target audience
        4. Commercial potential and market value
        
        Respond with valid JSON only:
        {{
            "category": "select from: E-commerce, Technology, News & Media, Education, Healthcare, Finance, Entertainment, Travel, Food & Beverage, Fashion, Real Estate, Sports, Gaming, Social Media, Business Services, Automotive, Legal, Non-profit, Government, Personal Blog, Other",
            "themes": ["2-3 specific themes"],
            "confidence": 0.85,
            "reasoning": "brief explanation",
            "recommended": true/false,
            "commercial_potential": "high/medium/low"
        }}
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are an expert domain analyst specializing in web categorization and commercial valuation. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.2
                }
                
                async with session.post(self.openai_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        # Clean and parse AI response
                        ai_response = ai_response.strip()
                        if ai_response.startswith('```json'):
                            ai_response = ai_response[7:-3]
                        elif ai_response.startswith('```'):
                            ai_response = ai_response[3:-3]
                        
                        ai_data = json.loads(ai_response)
                        
                        return {
                            "thematic_analysis_result": json.dumps(ai_data),
                            "ai_category": ai_data.get("category", "Other"),
                            "ai_confidence": ai_data.get("confidence", 0.5),
                            "ai_description": ai_data.get("reasoning", "AI analysis completed"),
                            "recommended": ai_data.get("recommended", False)
                        }
                        
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return None
    
    async def _call_anthropic_api(self, domain: str) -> Dict:
        """Call Anthropic Claude API for AI analysis"""
        
        prompt = f"""
        Analyze the domain "{domain}" for thematic categorization and commercial potential.
        
        Provide analysis as JSON:
        {{
            "category": "primary category",
            "themes": ["relevant themes"],
            "confidence": 0.0-1.0,
            "reasoning": "explanation",
            "recommended": boolean
        }}
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": self.anthropic_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                
                data = {
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 300,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                
                async with session.post(self.anthropic_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["content"][0]["text"]
                        
                        # Parse response
                        ai_data = json.loads(ai_response)
                        
                        return {
                            "thematic_analysis_result": json.dumps(ai_data),
                            "ai_category": ai_data.get("category", "Other"),
                            "ai_confidence": ai_data.get("confidence", 0.5),
                            "ai_description": ai_data.get("reasoning", "AI analysis completed"),
                            "recommended": ai_data.get("recommended", False)
                        }
                        
        except Exception as e:
            print(f"Anthropic API error: {str(e)}")
            return None
    
    def _get_default_ai_result(self) -> Dict:
        """Get default AI result when analysis fails"""
        return {
            "thematic_analysis_result": json.dumps({
                "category": "Other",
                "themes": ["unknown"],
                "confidence": 0.1,
                "analysis_method": "fallback",
                "error": "AI analysis unavailable",
                "recommended": False
            }),
            "ai_category": "Other",
            "ai_confidence": 0.1,
            "ai_description": "AI analysis could not be completed - using fallback categorization",
            "recommended": False
        }

# Global instance
ai_analyzer = AIAnalyzer()

