# Neopets-SDB-Splitter
This script takes HTML files of pages of your SDB that you've downloaded and divides them into 25 page segments for ease of copy-pasting said segments into Jellyneo's price checker.

# HOW TO USE 
Name it something like "sdb page source" 
Paste this into the box under URL Name
javascript:(function() {     const source = document.documentElement.outerHTML;     const filename = document.title.replace(/\s+/g, '_') + '_source.html';     const blob = new Blob([source], {type: 'text/plain'});     const link = document.createElement('a');     link.download = filename;     link.href = URL.createObjectURL(blob);     link.click(); })();
