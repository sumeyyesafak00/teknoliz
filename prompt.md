# Project: TechAnalyzer AI - YouTube Review & Sentiment Analysis

## 1. Project Overview
This is a web application designed to analyze technological products based on YouTube comments using AI. Users can search for products, fetch comments from the top relevant Turkish YouTube review videos, and get an AI-generated analysis.

## 2. Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla or modern ES6+)
- **Backend:** Python + Django
- **Database:** Supabase (PostgreSQL)
- **AI Integration:** Google Gemini API
- **Workflow:** Vibe Coding via Antigravity

## 3. Core Features
- **Product Search:** A search bar to find technological products.
- **YouTube Integration:** Automatically identify the top-ranked Turkish review video for the searched product and fetch comments via YouTube Data API.
- **AI Sentiment Analysis:** Use Gemini API to process comments and generate a comprehensive summary (pros, cons, overall sentiment).
- **Product Comparison:** Enable users to compare analysis results of two different products side-by-side.
- **UI/UX Consistency:** Build the interface based on the provided reference images (dark mode, minimalist, sleek).

## 4. Technical Instructions
### Frontend
- Follow the visual style of the attached images (Modern, dark-themed).
- Implement a responsive layout.
- Use AJAX/Fetch API to communicate with the Django backend.

### Backend (Django)
- **YouTube Module:** Create a service to search for videos and fetch comments.
- **Gemini Module:** Create a prompt engineering layer to send comments to Gemini and receive structured analysis.
- **Database (Supabase):** Store search history, cached analysis results, and user preferences.

## 5. Development Roadmap (Step-by-Step)
1. **Phase 1:** Setup Django project structure and Supabase connection.
2. **Phase 2:** Implement YouTube Data API to fetch comments based on search queries.
3. **Phase 3:** Integrate Gemini API to analyze the fetched text data.
4. **Phase 4:** Build the frontend UI matching the reference screenshots.
5. **Phase 5:** Implement the comparison logic and finalize the dashboard.

## 6. Context for AI
- Focus on Turkish language processing.
- Ensure the Gemini prompt asks for specific categories: "User Satisfaction," "Common Technical Issues," and "Value for Money."
