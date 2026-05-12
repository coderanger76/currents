"""
Email parser module for extracting rental data from Craigslist emails
"""

import re
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime


class RentalParser:
    def __init__(self):
        """Initialize the rental parser"""
        pass

    def parse_rental_email(self, email_data):
        """
        Parse a Craigslist rental email and extract relevant information

        Args:
            email_data: Dictionary containing email information from EmailFetcher

        Returns:
            Dictionary with parsed rental data or None if parsing fails
        """
        try:
            body = email_data.get('body', '')
            subject = email_data.get('subject', '')
            received_date = email_data.get('received_date', datetime.now())

            # Extract data from email
            location = self._extract_location(body, subject)
            price = self._extract_price(body, subject)
            sqft = self._extract_sqft(body)
            bedroom_count = self._extract_bedroom_count(body, subject)
            post_url = self._extract_url(body)

            # Generate unique ID for this listing
            listing_id = self._generate_listing_id(post_url, price, location)

            rental_data = {
                'listing_id': listing_id,
                'location': location,
                'price': price,
                'sqft': sqft,
                'bedroom_count': bedroom_count,
                'received_date': received_date,
                'subject': subject,
                'url': post_url,
                'email_id': email_data.get('id', '')
            }

            return rental_data

        except Exception as e:
            print(f"✗ Error parsing email: {e}")
            return None

    def _extract_location(self, body, subject):
        """
        Extract location/neighborhood from email
        Looks for specific Santa Clarita area communities in:
        1. Main text line (e.g., "$price - 1br - 893ft2 - ...")
        2. AHREF link text
        3. Parentheses after link (e.g., "(Canyon Country)" or "(18414 W. Jakes Way, Canyon Country, CA)")
        """
        # Communities to search for (case-insensitive)
        target_communities = [
            'Newhall',
            'Canyon Country',
            'Valencia',
            'Stevenson Ranch',
            'Palmdale',
            'Saugus',
            'Santa Clarita'
        ]

        # Create regex pattern to match any of these communities (case-insensitive)
        community_pattern = '|'.join([re.escape(community) for community in target_communities])

        # Function to find community in text
        def find_community(text):
            if not text:
                return None
            match = re.search(f'({community_pattern})', text, re.IGNORECASE)
            if match:
                # Return with proper capitalization from our list
                matched_text = match.group(1).lower()
                for community in target_communities:
                    if community.lower() == matched_text:
                        return community
            return None

        # Strategy 1: Parse HTML and look in different parts
        if '<' in body and '>' in body:
            soup = BeautifulSoup(body, 'html.parser')

            # Check all links (AHREF)
            for link in soup.find_all('a', href=True):
                link_text = link.get_text()
                location = find_community(link_text)
                if location:
                    return location

                # Also check the href URL itself
                href = link.get('href', '')
                location = find_community(href)
                if location:
                    return location

            # Check text in parentheses throughout the document
            full_text = soup.get_text()
            parentheses_matches = re.findall(r'\(([^)]+)\)', full_text)
            for paren_text in parentheses_matches:
                location = find_community(paren_text)
                if location:
                    return location

            # Check lines with price format: $price - 1br - sqft - ...
            price_lines = re.findall(r'\$\d+[,\d]*\s*[-–]\s*\d+br[^\n]*', full_text, re.IGNORECASE)
            for line in price_lines:
                location = find_community(line)
                if location:
                    return location

        # Strategy 2: Check plain text body
        location = find_community(body)
        if location:
            return location

        # Strategy 3: Check subject line
        location = find_community(subject)
        if location:
            return location

        return 'UNDETERMINED'

    def _extract_price(self, body, subject):
        """Extract rental price from email"""
        # Look for price patterns like $2000, $2,000, etc.
        price_patterns = [
            r'\$([0-9,]+)',  # Standard price format
            r'([0-9,]+)\s*(?:/mo|per month|monthly)',  # Alternative formats
        ]

        # Try subject first (usually has the price)
        for pattern in price_patterns:
            matches = re.findall(pattern, subject)
            for match in matches:
                price = match.replace(',', '')
                try:
                    price_val = int(price)
                    # Sanity check: reasonable rent range
                    if 500 <= price_val <= 10000:
                        return price_val
                except ValueError:
                    continue

        # Try body
        for pattern in price_patterns:
            matches = re.findall(pattern, body[:1000])  # Check first 1000 chars
            for match in matches:
                price = match.replace(',', '')
                try:
                    price_val = int(price)
                    if 500 <= price_val <= 10000:
                        return price_val
                except ValueError:
                    continue

        return None

    def _extract_sqft(self, body):
        """Extract square footage from email"""
        # Look for sqft patterns
        sqft_patterns = [
            r'([0-9,]+)\s*(?:sq\.?\s*ft|sqft|square feet)',
            r'([0-9,]+)\s*ft[²2]',
        ]

        for pattern in sqft_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                sqft = match.group(1).replace(',', '')
                try:
                    sqft_val = int(sqft)
                    # Sanity check: reasonable sqft range
                    if 200 <= sqft_val <= 3000:
                        return sqft_val
                except ValueError:
                    continue

        return None

    def _extract_bedroom_count(self, body, subject):
        """Extract number of bedrooms from email"""
        # Look for bedroom patterns: "1 bedroom", "2br", "1 br", "1BR", etc.
        bedroom_patterns = [
            r'(\d+)\s*(?:bedroom|bed\s*room)',  # "1 bedroom", "2 bedroom"
            r'(\d+)\s*br\b',                     # "1br", "2br"
            r'(\d+)\s*-?\s*br\b',                # "1-br", "2 br"
        ]

        # Try subject first (usually has bedroom count)
        for pattern in bedroom_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                bedroom_count = int(match.group(1))
                # Sanity check: reasonable bedroom range
                if 1 <= bedroom_count <= 5:
                    return bedroom_count

        # Try body
        for pattern in bedroom_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                bedroom_count = int(match.group(1))
                if 1 <= bedroom_count <= 5:
                    return bedroom_count

        # Default to None if not found
        return None

    def _extract_url(self, body):
        """Extract Craigslist post URL from email"""
        # Look for Craigslist URLs
        url_pattern = r'https?://[a-z]+\.craigslist\.org/[^\s<>"]+\.html'
        match = re.search(url_pattern, body)
        if match:
            return match.group(0)

        # Try to find any craigslist link
        url_pattern = r'https?://[^\s<>"]*craigslist[^\s<>"]*'
        match = re.search(url_pattern, body)
        if match:
            return match.group(0)

        return None

    def _generate_listing_id(self, url, price, location):
        """
        Generate a unique ID for the listing
        Uses URL if available, otherwise creates hash from price + location + timestamp
        """
        if url:
            # Extract the Craigslist post ID from URL if possible
            post_id_match = re.search(r'/([0-9]+)\.html', url)
            if post_id_match:
                return f"cl_{post_id_match.group(1)}"

        # Fallback: create hash
        data_str = f"{url}_{price}_{location}"
        hash_id = hashlib.md5(data_str.encode()).hexdigest()[:12]
        return f"listing_{hash_id}"


if __name__ == "__main__":
    # Test the parser
    parser = RentalParser()

    # Sample test email
    test_email = {
        'id': '123',
        'subject': '1BR/1BA apartment (West LA) $2,500',
        'body': 'Beautiful 1 bedroom apartment in West LA. 750 sqft. $2500/month. https://losangeles.craigslist.org/wst/apa/123456789.html',
        'received_date': datetime.now()
    }

    result = parser.parse_rental_email(test_email)
    print("Parsed rental data:")
    for key, value in result.items():
        print(f"  {key}: {value}")
