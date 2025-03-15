import requests
import json
import os


class LinkedInShare:
    """
    A Python wrapper for the LinkedIn Share API.
    This class provides methods to post content to LinkedIn, including text, articles/URLs, and images/videos.
    """
    
    def __init__(self, access_token, person_urn=None):
        """
        Initialize the LinkedIn API wrapper with an OAuth 2.0 access token.
        
        Args:
            access_token (str): OAuth 2.0 access token with w_member_social scope
            person_urn (str, optional): Your LinkedIn Person URN (e.g., "urn:li:person:Hi1z4OfXkc")
        """
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Set person URN if provided, otherwise fetch it
        self.person_urn = person_urn
        if not self.person_urn:
            self.get_person_urn()
    
    def get_person_urn(self):
        """
        Get the profile information of the authenticated user to retrieve the Person URN.
        
        Returns:
            dict: Profile information
        """
        url = f"{self.base_url}/userinfo"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        profile_data = response.json()
        self.person_urn = f"urn:li:person:{profile_data['sub']}"
        return profile_data
    
    def post_text(self, text, visibility="PUBLIC"):
        """
        Create a simple text post on LinkedIn.
        
        Args:
            text (str): The text content of the post
            visibility (str): Visibility of the post, either "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Response from the API including status code and headers
        """
        if not self.person_urn:
            raise ValueError("Person URN is required. Either provide it during initialization or call get_profile() first.")
            
        url = f"{self.base_url}/ugcPosts"
        
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "post_id": response.headers.get('X-RestLi-Id') if response.status_code == 201 else None
        }
        
        if response.status_code != 201:
            result["error"] = response.text
        
        return result
    
    def post_article(self, text, article_url, title=None, description=None, visibility="PUBLIC"):
        """
        Create a post with an article or URL on LinkedIn.
        
        Args:
            text (str): The text content of the post
            article_url (str): URL to share
            title (str, optional): Custom title for the article
            description (str, optional): Custom description for the article
            visibility (str): Visibility of the post, either "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Response from the API including status code and headers
        """
        if not self.person_urn:
            raise ValueError("Person URN is required. Either provide it during initialization or call get_profile() first.")
            
        url = f"{self.base_url}/ugcPosts"
        
        media = {
            "status": "READY",
            "originalUrl": article_url
        }
        
        if title:
            media["title"] = {"text": title}
        
        if description:
            media["description"] = {"text": description}
        
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [media]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "post_id": response.headers.get('X-RestLi-Id') if response.status_code == 201 else None
        }
        
        if response.status_code != 201:
            result["error"] = response.text
        
        return result
    
    def register_upload(self, media_type="image"):
        """
        Register an image or video upload with LinkedIn.
        
        Args:
            media_type (str): Either "image" or "video"
            
        Returns:
            tuple: (upload_url, asset_id) or None if registration fails
        """
        if not self.person_urn:
            raise ValueError("Person URN is required. Either provide it during initialization or call get_profile() first.")
            
        url = f"{self.base_url}/assets?action=registerUpload"
        
        recipe = "urn:li:digitalmediaRecipe:feedshare-image" if media_type == "image" else "urn:li:digitalmediaRecipe:feedshare-video"
        
        payload = {
            "registerUploadRequest": {
                "recipes": [recipe],
                "owner": self.person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            print(f"Error registering upload: {response.status_code}")
            print(response.text)
            return None
        
        data = response.json()
        
        try:
            upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_id = data["value"]["asset"]
            return upload_url, asset_id
        except KeyError as e:
            print(f"Unexpected response format: {e}")
            print(data)
            return None
    
    def upload_media(self, upload_url, file_path):
        """
        Upload an image or video file to LinkedIn.
        
        Args:
            upload_url (str): URL obtained from register_upload
            file_path (str): Path to the local image or video file
            
        Returns:
            bool: True if upload was successful
        """
        with open(file_path, 'rb') as file:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            response = requests.post(upload_url, headers=headers, data=file)
            
            if response.status_code >= 200 and response.status_code < 300:
                return True
            else:
                print(f"Error uploading media: {response.status_code}")
                print(response.text)
                return False
    
    def post_image(self, text, image_path, title=None, description=None, visibility="PUBLIC"):
        """
        Create a post with an image on LinkedIn.
        
        Args:
            text (str): The text content of the post
            image_path (str): Path to the local image file
            title (str, optional): Custom title for the image
            description (str, optional): Custom description for the image
            visibility (str): Visibility of the post, either "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Response from the API including status code and headers
        """
        if not self.person_urn:
            raise ValueError("Person URN is required. Either provide it during initialization or call get_profile() first.")
            
        # Register upload
        upload_result = self.register_upload(media_type="image")
        if not upload_result:
            return {"status_code": 500, "error": "Failed to register image upload"}
        
        upload_url, asset_id = upload_result
        
        # Upload image
        upload_success = self.upload_media(upload_url, image_path)
        if not upload_success:
            return {"status_code": 500, "error": "Failed to upload image"}
        
        # Create post with the uploaded image
        url = f"{self.base_url}/ugcPosts"
        
        media = {
            "status": "READY",
            "media": asset_id
        }
        
        if title:
            media["title"] = {"text": title}
        
        if description:
            media["description"] = {"text": description}
        
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [media]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "post_id": response.headers.get('X-RestLi-Id') if response.status_code == 201 else None
        }
        
        if response.status_code != 201:
            result["error"] = response.text
        
        return result
    
    def post_video(self, text, video_path, title=None, description=None, visibility="PUBLIC"):
        """
        Create a post with a video on LinkedIn.
        
        Args:
            text (str): The text content of the post
            video_path (str): Path to the local video file
            title (str, optional): Custom title for the video
            description (str, optional): Custom description for the video
            visibility (str): Visibility of the post, either "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Response from the API including status code and headers
        """
        if not self.person_urn:
            raise ValueError("Person URN is required. Either provide it during initialization or call get_profile() first.")
            
        # Register upload
        upload_result = self.register_upload(media_type="video")
        if not upload_result:
            return {"status_code": 500, "error": "Failed to register video upload"}
        
        upload_url, asset_id = upload_result
        
        # Upload video
        upload_success = self.upload_media(upload_url, video_path)
        if not upload_success:
            return {"status_code": 500, "error": "Failed to upload video"}
        
        # Create post with the uploaded video
        url = f"{self.base_url}/ugcPosts"
        
        media = {
            "status": "READY",
            "media": asset_id
        }
        
        if title:
            media["title"] = {"text": title}
        
        if description:
            media["description"] = {"text": description}
        
        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "VIDEO",
                    "media": [media]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "post_id": response.headers.get('X-RestLi-Id') if response.status_code == 201 else None
        }
        
        if response.status_code != 201:
            result["error"] = response.text
        
        return result