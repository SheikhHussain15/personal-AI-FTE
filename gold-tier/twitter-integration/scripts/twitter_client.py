#!/usr/bin/env python3
"""
Twitter API Client

Low-level client for Twitter API v2 operations.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

import tweepy
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class TwitterClient:
    """Client for Twitter API v2."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
    ):
        """
        Initialize Twitter client.
        
        Args:
            api_key: Twitter API Key
            api_secret: Twitter API Secret
            access_token: Access Token
            access_token_secret: Access Token Secret
            bearer_token: Bearer Token for OAuth 2.0
        """
        # Load from environment if not provided
        load_dotenv()
        
        self.api_key = api_key or os.getenv('TWITTER_API_KEY', '')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET', '')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN', '')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN', '')
        
        # Initialize clients
        self._client_v2 = None
        self._api_v1 = None
    
    @property
    def client_v2(self) -> tweepy.Client:
        """Get Twitter API v2 client."""
        if self._client_v2 is None:
            self._client_v2 = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True,
            )
        return self._client_v2
    
    @property
    def api_v1(self) -> tweepy.API:
        """Get Twitter API v1.1 client (for media upload)."""
        if self._api_v1 is None:
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret,
            )
            self._api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
        return self._api_v1
    
    def get_me(self) -> Dict[str, Any]:
        """Get authenticated user info."""
        user = self.client_v2.get_me()
        return {
            'id': user.data.id,
            'name': user.data.name,
            'username': user.data.username,
        }
    
    def create_tweet(
        self,
        text: str,
        media_url: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a tweet.
        
        Args:
            text: Tweet text (max 280 chars)
            media_url: Optional media URL to upload
            reply_to: Optional tweet ID to reply to
            
        Returns:
            Tweet result
        """
        media_ids = None
        
        if media_url:
            media_ids = [self._upload_media(media_url)]
        
        tweet = self.client_v2.create_tweet(
            text=text,
            media_ids=media_ids,
            in_reply_to_tweet_id=reply_to,
        )
        
        return {
            'success': True,
            'tweet_id': tweet.data.id,
            'text': tweet.data.text,
            'permalink': f'https://twitter.com/i/web/status/{tweet.data.id}',
        }
    
    def create_thread(
        self,
        tweets: List[str],
        media_urls: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a tweet thread.
        
        Args:
            tweets: List of tweet texts
            media_urls: Optional list of media URLs
            
        Returns:
            Thread result with tweet IDs
        """
        if not tweets:
            raise ValueError('At least one tweet required')
        
        results = []
        reply_to = None
        
        for i, text in enumerate(tweets):
            media_url = media_urls[i] if media_urls and i < len(media_urls) else None
            
            result = self.create_tweet(text=text, media_url=media_url, reply_to=reply_to)
            results.append(result)
            
            # Next tweet replies to this one
            reply_to = result['tweet_id']
        
        return {
            'success': True,
            'tweet_count': len(results),
            'tweets': results,
            'first_tweet': results[0]['tweet_id'],
            'permalink': results[0]['permalink'],
        }
    
    def _upload_media(self, url_or_path: str) -> str:
        """Upload media and return media ID."""
        import requests
        from io import BytesIO
        
        # Check if URL or local path
        if url_or_path.startswith('http'):
            response = requests.get(url_or_path)
            media_file = BytesIO(response.content)
        else:
            media_file = open(url_or_path, 'rb')
        
        # Upload media
        media = self.api_v1.media_upload(filename='media', file=media_file)
        
        return media.media_id
    
    def get_mentions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent mentions.
        
        Args:
            limit: Number of mentions to fetch
            
        Returns:
            List of mention tweets
        """
        me = self.get_me()
        
        mentions = self.client_v2.get_users_mentions(
            id=me['id'],
            max_results=min(limit, 100),
            tweet_fields=['created_at', 'author_id', 'text', 'public_metrics'],
            user_fields=['name', 'username'],
        )
        
        if not mentions.data:
            return []
        
        results = []
        for tweet in mentions.data:
            results.append({
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'author_id': tweet.author_id,
                'metrics': tweet.public_metrics,
            })
        
        return results
    
    def get_dms(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent direct messages.
        
        Note: DM API access requires elevated/enterprise access.
        """
        try:
            # Get DM events
            events = self.client_v2.get_direct_messages(
                max_results=min(limit, 100),
                message_fields=['text', 'created_at'],
            )
            
            if not events.data:
                return []
            
            results = []
            for dm in events.data:
                results.append({
                    'id': dm.id,
                    'text': dm.text,
                    'created_at': dm.created_at.isoformat() if dm.created_at else None,
                })
            
            return results
            
        except Exception as e:
            logger.warning(f'DM access not available: {e}')
            return []
    
    def search_tweets(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for tweets.
        
        Args:
            query: Search query (Twitter search syntax)
            limit: Number of tweets to fetch
            
        Returns:
            List of tweets
        """
        tweets = self.client_v2.search_recent_tweets(
            query=query,
            max_results=min(limit, 100),
            tweet_fields=['created_at', 'author_id', 'text', 'public_metrics'],
        )
        
        if not tweets.data:
            return []
        
        results = []
        for tweet in tweets.data:
            results.append({
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'author_id': tweet.author_id,
                'metrics': tweet.public_metrics,
            })
        
        return results
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get metrics for a tweet."""
        tweet = self.client_v2.get_tweet(
            id=tweet_id,
            tweet_fields=['public_metrics', 'created_at'],
        )
        
        if not tweet.data:
            return {'error': 'Tweet not found'}
        
        return {
            'tweet_id': tweet_id,
            'metrics': tweet.data.public_metrics,
            'created_at': tweet.data.created_at.isoformat() if tweet.data.created_at else None,
        }
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> Dict[str, Any]:
        """Reply to a tweet."""
        return self.create_tweet(text=text, reply_to=tweet_id)
    
    def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet."""
        me = self.get_me()
        result = self.client_v2.like(tweet_id=tweet_id, user_auth=True)
        
        return {
            'success': True,
            'tweet_id': tweet_id,
            'liked': result.data.get('liked', False),
        }
    
    def retweet(self, tweet_id: str) -> Dict[str, Any]:
        """Retweet a tweet."""
        me = self.get_me()
        result = self.client_v2.retweet(tweet_id=tweet_id, user_auth=True)
        
        return {
            'success': True,
            'tweet_id': tweet_id,
            'retweeted': result.data.get('retweeted', False),
        }


# Convenience functions

def get_client() -> TwitterClient:
    """Get configured Twitter client."""
    return TwitterClient()


if __name__ == '__main__':
    # Test connection
    logging.basicConfig(level=logging.INFO)
    
    client = get_client()
    
    try:
        print('Testing Twitter connection...')
        me = client.get_me()
        print(f'✅ Connected as: @{me["username"]} ({me["name"]})')
        
        # Get recent mentions
        mentions = client.get_mentions(limit=5)
        print(f'\nRecent mentions: {len(mentions)}')
        for m in mentions[:3]:
            print(f'  - {m["text"][:50]}...')
        
    except Exception as e:
        print(f'❌ Error: {e}')
