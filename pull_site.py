import requests
from bs4 import BeautifulSoup
import hashlib
import os

pages = ['/', '/blog', '/services',  '/products', '/contact']
base_url = 'https://motiongis.framer.website'
hash_file = 'page_hashes.txt'
updated = False

# Load previous hashes
if os.path.exists(hash_file):
    with open(hash_file, 'r') as f:
        old_hashes = dict(line.strip().split() for line in f)
else:
    old_hashes = {}

new_hashes = {}

for page in pages:
    url = f'{base_url}{page}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove elements with ID "logo-container"
    logo_container = soup.find(id='__framer-badge-container')
    if logo_container:
        logo_container.decompose()

    # Convert absolute links to relative links
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(base_url):
            link['href'] = href.replace(base_url, '')


    # Generate hash of the page content after modifications
    page_hash = hashlib.sha256(soup.prettify().encode('utf-8')).hexdigest()
    new_hashes[page] = page_hash

    # Save page if it has changed or if it's the first run
    if page not in old_hashes or old_hashes[page] != page_hash:
        updated = True
        page_path = f'website{page if page != "/" else "/index"}.html'
        os.makedirs(os.path.dirname(page_path), exist_ok=True)
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

# If any page was updated, save new hashes and commit changes
if updated:
    with open(hash_file, 'w') as f:
        for page, page_hash in new_hashes.items():
            f.write(f'{page} {page_hash}\n')

    # Commit and push changes to the repository
    os.system('git config user.name "GitHub Actions"')
    os.system('git config user.email "actions@github.com"')
    os.system('git add .')
    os.system('git commit -m "Update website snapshots"')
    os.system('git push')
