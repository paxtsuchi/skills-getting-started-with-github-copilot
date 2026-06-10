"""Tests for the FastAPI application endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns the list of all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Verify we get activities back
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Verify known activities are present
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        
    def test_get_activities_contains_activity_details(self, client):
        """Test that activity objects contain expected fields."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
    def test_signup_verifies_signup_was_recorded(self, client):
        """Test that signup is actually recorded in the activity."""
        email = "testuser@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signup by getting activities
        response = client.get("/activities")
        activities = response.json()
        
        assert email in activities["Programming Class"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup returns 400 error."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_missing_email_parameter(self, client):
        """Test that signup without email parameter returns an error."""
        response = client.post("/activities/Chess Club/signup")
        
        # FastAPI will return 422 for missing required parameter
        assert response.status_code == 422

    def test_signup_to_different_activities(self, client):
        """Test that a student can sign up for multiple different activities."""
        email = "multiactivity@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        activities = response.json()
        
        assert email in activities["Art Club"]["participants"]
        assert email in activities["Soccer Team"]["participants"]
