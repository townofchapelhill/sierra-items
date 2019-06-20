# items
Scripts that organize library item information for the Chapel Hill Open Data portal and dashboards. Data is retrieved from the Sierra API. More information can be found at https://sandbox.iii.com/docs/Content/titlePage.htm.

<strong>To any future Open Data devs:</strong>

"catalog_checkouts.py" is a script designed to find matches between the items table and the bibs table in the Sierra database.  It does successfully find those matches, but I could never get it to run faster than 19.5 hours.  It doesn't run on the server because of how much RAM it eats up (see: my spaghetti code).  If you're having an extra slow week and looking for a challenge then give it a shot, but only if you have literally nothing else to do