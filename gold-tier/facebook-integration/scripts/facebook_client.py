#!/usr/bin/env python3
"""
Facebook/Instagram Graph API Client

Official Meta Graph API client for Facebook Pages and Instagram Business.
No Playwright - pure API integration.
"""

import io
import json
import logging
import os
import sys
import requests
from typing import Any, Dict, List, Optional
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


logger = logging.getLogger(__name__)

# Graph API base URL
GRAPH_API_BASE = 'https://graph.facebook.com/v19.0'


def load_facebook_env():
    """Load .env.facebook from project root or current directory."""
    # Try to find .env.facebook in project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    
    env_files = [
        project_root / '.env.facebook',
        Path.cwd() / '.env.facebook',
        find_dotenv('.env.facebook'),
    ]
    
    for env_file in env_files:
        if env_file and Path(env_file).exists():
            load_dotenv(str(env_file))
            logger.debug(f'Loaded environment from: {env_file}')
            return
    
    # Fallback to standard find_dotenv
    load_dotenv(find_dotenv())


class FacebookClient:
    """Client for Meta Graph API (Facebook/Instagram)."""
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        page_id: Optional[str] = None,
        page_token: Optional[str] = None,
        instagram_id: Optional[str] = None,
        api_version: str = 'v19.0',
    ):
        """
        Initialize Facebook client.
        
        All parameters are optional and will be loaded from .env.facebook if not provided.
        
        Args:
            access_token: User or page access token
            page_id: Facebook Page ID
            page_token: Page-specific access token
            instagram_id: Instagram Business Account ID
            api_version: Graph API version
        """
        # Load from environment if not provided
        load_facebook_env()
        
        self.access_token = access_token or os.getenv('META_ACCESS_TOKEN', '')
        self.page_id = page_id or os.getenv('META_PAGE_ID', '')
        self.page_token = page_token or os.getenv('META_PAGE_TOKEN', self.access_token)
        self.instagram_id = instagram_id or os.getenv('META_INSTAGRAM_ID', '')
        self.api_version = api_version or os.getenv('META_API_VERSION', 'v19.0')
        
        # Update base URL with API version
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        
        self.session = requests.Session()
        
        # Validate configuration
        if not self.access_token:
            logger.error('META_ACCESS_TOKEN not configured. Run facebook_auth.py first.')
            raise ValueError('Facebook access token not configured')
    
    def _get(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        if params is None:
            params = {}
        
        # Add access token if not already in params
        if 'access_token' not in params:
            params['access_token'] = self.access_token
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            result = response.json()
            
            if 'error' in result:
                error = result['error']
                error_msg = error.get('message', 'Unknown error')
                error_code = error.get('code', 'UNKNOWN')
                
                # Handle token expiration
                if error_code == 190 or error_code == 100:
                    logger.error(f'Token expired or invalid: {error_msg}')
                    raise Exception(f'Token expired: {error_msg}')
                
                logger.error(f'Graph API error ({error_code}): {error_msg}')
                raise Exception(f'Graph API error: {error_msg}')
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error('Request timeout')
            raise Exception('Request timeout')
        except requests.exceptions.RequestException as e:
            logger.error(f'Request error: {e}')
            raise Exception(f'Request error: {e}')
    
    def _post(self, url: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request."""
        if data is None:
            data = {}
        
        # Add access token if not already in data
        if 'access_token' not in data:
            data['access_token'] = self.access_token
        
        try:
            if files:
                response = self.session.post(url, data=data, files=files, timeout=60)
            else:
                response = self.session.post(url, data=data, timeout=30)
            
            result = response.json()
            
            if 'error' in result:
                error = result['error']
                error_msg = error.get('message', 'Unknown error')
                error_code = error.get('code', 'UNKNOWN')
                
                logger.error(f'Graph API error ({error_code}): {error_msg}')
                raise Exception(f'Graph API error: {error_msg}')
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error('Request timeout')
            raise Exception('Request timeout')
        except requests.exceptions.RequestException as e:
            logger.error(f'Request error: {e}')
            raise Exception(f'Request error: {e}')
    
    def get_page_info(self, page_id: Optional[str] = None) -> Dict[str, Any]:
        """Get Facebook Page information."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        return self._get(f'{self.base_url}/{pid}', {'fields': 'id,name,about,website,followers_count'})
    
    def get_page_posts(self, page_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get page posts."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        result = self._get(
            f'{self.base_url}/{pid}/posts',
            {'limit': limit, 'fields': 'id,message,created_time,permalink_url,full_picture'}
        )
        return result.get('data', [])
    
    def get_page_messages(self, page_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get page inbox messages."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        result = self._get(
            f'{self.base_url}/{pid}/conversations',
            {
                'limit': limit,
                'fields': 'id,link,messages.limit(5){from,message,created_time}',
                'folder': 'inbox',
            }
        )
        return result.get('data', [])
    
    def get_post_comments(self, post_id: str, limit: int = 10) -> List[Dict]:
        """Get comments on a post."""
        result = self._get(
            f'{self.base_url}/{post_id}/comments',
            {'limit': limit, 'fields': 'id,from,message,created_time,like_count'}
        )
        return result.get('data', [])
    
    def create_page_post(
        self,
        message: str,
        link: Optional[str] = None,
        image_url: Optional[str] = None,
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a post on Facebook Page."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        data = {
            'message': message,
        }
        
        if link:
            data['link'] = link
        
        if image_url:
            # Post photo with message using attached_media
            data['attached_media'] = json.dumps([{'media_url': image_url}])
        
        result = self._post(f'{self.base_url}/{pid}/feed', data)
        
        return {
            'success': True,
            'post_id': result.get('id'),
            'permalink': f'https://facebook.com/{result.get("id")}',
        }
    
    def create_photo_post(
        self,
        photo_url: str,
        caption: str,
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a photo post on Facebook Page."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        data = {
            'url': photo_url,
            'caption': caption,
        }
        
        result = self._post(f'{self.base_url}/{pid}/photos', data)
        
        return {
            'success': True,
            'post_id': result.get('id'),
            'permalink': result.get('post_id', f'https://facebook.com/{result.get("id")}'),
        }
    
    def send_page_message(
        self,
        recipient_id: str,
        message: str,
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message via Page (Messenger)."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        data = {
            'recipient': json.dumps({'id': recipient_id}),
            'message': json.dumps({'text': message}),
            'messaging_type': 'RESPONSE',
        }
        
        result = self._post(f'{self.base_url}/{pid}/messages', data)
        
        return {
            'success': True,
            'message_id': result.get('message_id'),
        }
    
    def get_page_insights(
        self,
        metrics: Optional[List[str]] = None,
        period: str = 'day',
        page_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get page insights/analytics."""
        pid = page_id or self.page_id
        
        if not pid:
            raise ValueError('Page ID not configured')
        
        if metrics is None:
            metrics = ['page_impressions', 'page_engaged_users', 'page_post_engagements']
        
        result = self._get(
            f'{self.base_url}/{pid}/insights',
            {
                'metric': ','.join(metrics),
                'period': period,
            }
        )
        
        insights = {}
        for item in result.get('data', []):
            insights[item['name']] = {
                'values': item.get('values', []),
                'period': item.get('period', 'one_time'),
                'title': item.get('title', ''),
            }
        
        return insights
    
    # Instagram methods
    
    def get_instagram_info(self, instagram_id: Optional[str] = None) -> Dict[str, Any]:
        """Get Instagram Business Account information."""
        ig_id = instagram_id or self.instagram_id
        
        if not ig_id:
            raise ValueError('Instagram Business Account ID not configured')
        
        return self._get(
            f'{self.base_url}/{ig_id}',
            {'fields': 'id,name,username,biography,website,profile_picture_url,followers_count,media_count'}
        )
    
    def get_instagram_media(self, instagram_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get Instagram media."""
        ig_id = instagram_id or self.instagram_id
        
        if not ig_id:
            raise ValueError('Instagram Business Account ID not configured')
        
        result = self._get(
            f'{self.base_url}/{ig_id}/media',
            {'limit': limit, 'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count'}
        )
        return result.get('data', [])
    
    def get_instagram_insights(
        self,
        metric: str = 'impressions',
        period: str = 'day',
        instagram_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get Instagram insights."""
        ig_id = instagram_id or self.instagram_id
        
        if not ig_id:
            raise ValueError('Instagram Business Account ID not configured')
        
        result = self._get(
            f'{self.base_url}/{ig_id}/insights',
            {'metric': metric, 'period': period}
        )
        
        insights = {}
        for item in result.get('data', []):
            insights[item['name']] = {
                'values': item.get('values', []),
                'period': item.get('period', 'one_time'),
            }
        
        return insights
    
    def create_instagram_post(
        self,
        image_url: str,
        caption: str,
        instagram_id: Optional[str] = None,
        is_carousel: bool = False,
        children: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create an Instagram post.
        
        Two-step process:
        1. Create media container
        2. Publish media
        """
        ig_id = instagram_id or self.instagram_id
        
        if not ig_id:
            raise ValueError('Instagram Business Account ID not configured')
        
        # Step 1: Create media container
        container_data = {
            'image_url': image_url,
            'caption': caption,
        }
        
        if is_carousel and children:
            container_data['media_type'] = 'CAROUSEL'
            container_data['children'] = ','.join(children)
        
        container_response = self._post(
            f'{self.base_url}/{ig_id}/media',
            container_data
        )
        
        creation_id = container_response.get('id')
        
        if not creation_id:
            raise Exception('Failed to create media container')
        
        # Step 2: Publish media
        publish_response = self._post(
            f'{self.base_url}/{ig_id}/media_publish',
            {'creation_id': creation_id}
        )
        
        published_media_id = publish_response.get('id')
        
        # Get permalink
        try:
            media_info = self._get(
                f'{self.base_url}/{published_media_id}',
                {'fields': 'permalink'}
            )
            permalink = media_info.get('permalink', '')
        except Exception:
            permalink = ''
        
        return {
            'success': True,
            'media_id': published_media_id,
            'permalink': permalink,
        }
    
    def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Reply to a comment."""
        data = {
            'message': message,
        }
        
        result = self._post(
            f'{self.base_url}/{comment_id}/comments',
            data
        )
        
        return {
            'success': True,
            'comment_id': result.get('id'),
        }
    
    def get_token_info(self) -> Dict[str, Any]:
        """Get info about current access token."""
        result = self._get(f'{self.base_url}/debug_token', {'input_token': self.access_token})
        return result.get('data', {})
    
    def refresh_token(self, app_id: str, app_secret: str) -> Optional[str]:
        """Refresh long-lived token."""
        result = self._get(
            f'{self.base_url}/oauth/access_token',
            {
                'grant_type': 'fb_exchange_token',
                'client_id': app_id,
                'client_secret': app_secret,
                'fb_exchange_token': self.access_token,
            }
        )
        
        if 'access_token' in result:
            return result['access_token']
        return None


# Convenience functions

def get_client() -> FacebookClient:
    """Get configured Facebook client."""
    return FacebookClient()


if __name__ == '__main__':
    # Test connection
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = FacebookClient()
        print('Testing Facebook connection...')
        
        # Get token info
        token_info = client.get_token_info()
        if token_info:
            print(f'✅ Token valid: {token_info.get("is_valid", False)}')
            print(f'   Expires: {token_info.get("expires_at", "Unknown")}')
        
        # Get page info
        if client.page_id:
            page_info = client.get_page_info()
            print(f'\n✅ Connected to Facebook Page: {page_info.get("name")}')
        
        # Get Instagram info
        if client.instagram_id:
            ig_info = client.get_instagram_info()
            print(f'\n✅ Connected to Instagram: @{ig_info.get("username")}')
        
        print('\n✅ Facebook/Instagram client ready!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print('\nRun facebook_auth.py to configure credentials')
