# Datasets

## Four-categories

To Dataset: Τυχαίες 4 κατηγορίες ή DC1 αποτελείται από 400 κόμβους του Twitter.
 Οι κόμβοι έχουν χωριστεί σε τέσσερεις τυχαίες κατηγορίες, τουρισμός, πολιτική, εστίαση και εκπαίδευση. 
 Κάθε κατηγορία αποτελείται από 100 κόμβους. 
 Για κάθε κόμβο συλλέχθηκαν οι εξής πληροφορίες (Νοέμβριος 2020 – Ιανουάριος 2021):
- Username
- Profile name
- Profile description
- Πρόσφατο tweet
- Πρόσφατα 10 tweets
- Πρόσφατα 100 tweets
- Αριθμός tweets
- Αριθμός φίλων
- Αριθμός ακολούθων
- Κατηγορία

Ο φάκελος αυτός αποτελείται από 3 αρχεία:
-  Dataset-Analysis.ipynb
- four-categories-training-set.csv
- four-categories-validation-set.csv

Το αρχείο Dataset-analysis.ipynb περίεχει κώδικα με τον οποίο υπολογίσαμε στατιστικά
για το dataset.


---
## Greek Politicians
Ο φάκελος Greek Politicians αποτελείται από δύο datasets.
### Classification
Συνολικά έχουμε 400 κόμβους λογαριασμούς twitter οι οποιοι έχουν χωριστεί σε
training set και validation set (300-100). Για κάθε λογαριασμό έχουν συλλεχθεί τα εξής:
- username
- profile_name
- description
- recent_status
- recent_10_statuses
- recent_100_statuses
- statuses_count
- friends_count
- followers_count
- category


Ο φάκελος classification περιλαμβάνει τα εξής αρχεία:
- Members of the Greek Parliament Dataset Collection.ipynb
- Members of the Greek Parliament Dataset Statistics.ipynb
- parliament_members_training_set.csv
- parliament_members_validation_set.csv
- parliament_members_training_set_enhanced.csv
- parliament_members_validation_set_enhanced.csv

Τα αρχεία xx_xx.ipynb περίεχουν κώδικες για την συλλογή και την εξαγωγή στατιστικών.

Επίσης στα αρχεία x_x_x_x_enhanced.csv έχουμε υπολογίσει τους αριθμούς 
των 1000 φίλων, 1000 ακολούθων και των mentions από τα 100 statuses που είναι βουλευτές, χρησιμοποιώντας
μοντέλα μηχανικής μάθησης που χαρακτηρίζουν τους κόμβους ως βουλευτές ή όχι,
με βάση το όνομα και την περιγραφή προφίλ τους. 

### search-tool
O φάκελος search-tool περιλαμάνει τα εξής αρχεία:
- parliament-members-2015.csv
- parliament-members-analysis-search.csv

Το αρχείο parliament-members-2015.csv αποτελείται από τους 300 βουλευτές
του ελλινικού κοινοβουλίου του 2015. Για κάθε βουλευτή έχουμε τα εξής στοιχεία:
- Name (Long)
- Surname
- Name
- Party
- Twitter Handle

Το αρχείο parliament-members-analysis-search.csv περιέχει τα αποτελέσματα
αναζήτησης με τα οποία πραγματιοποιήθηκε το failure analysis.


---

## Hotels
Ο φάκελος Greek Politicians αποτελείται από δύο datasets.

### classification
Συνολικά έχουμε 250 κόμβους λογαριασμούς twitter οι οποιοι έχουν χωριστεί σε
training set και validation set (200-50). Για κάθε λογαριασμό έχουν συλλεχθεί τα εξής:
- username
- profile_name
- description
- recent_status
- recent_10_statuses
- recent_100_statuses
- statuses_count
- friends_count
- followers_count
- category

Ο φάκελος classification περιλαμβάνει τα εξής αρχεία:
- Dataset-Greek-Hotels-Classification.ipynb
- Dataset-Hotels-Satistics.ipynb
- hotels-classification.csv
- hotels-training-set.csv
- hotels-training-set-enhanced.csv
- hotels-validation-set.csv
- hotels-validation-set-enhanced.csv

Τα αρχεία xx_xx.ipynb περίεχουν κώδικες για την συλλογή και την εξαγωγή στατιστικών.

Το αρχείο hotels-classification.csv περιέχει τον κώδικα για την συλλογή του dataset.

Επίσης στα αρχεία x_x_x_x_enhanced.csv έχουμε υπολογίσει τους αριθμούς 
των 1000 φίλων, 1000 ακολούθων και των mentions από τα 100 statuses που είναι ξενοδοχεία, χρησιμοποιώντας
μοντέλα μηχανικής μάθησης που χαρακτηρίζουν τους κόμβους ως ξενοδοχεία ή όχι,
με βάση το όνομα και την περιγραφή προφίλ τους. 

### search-tool
O φάκελος search-tool περιλαμάνει τα εξής αρχεία:
- Dataset-Analysis.csv
- greek-hotels-2018-search.csv

Το αρχείο greek-hotels-2018-search.csv αποτελείται από τους 100 ξενοδοχεία. 
Για κάθε βουλευτή έχουμε τα εξής στοιχεία:
- hotel_city
- hotel_name
- hotel_website
- twitter
- facebook

Το αρχείο Dataset-Analysis.csv περιέχει τα αποτελέσματα
αναζήτησης με τα οποία πραγματιοποιήθηκε το failure analysis.


---
## poi-hania
To dataset αποτελείται από 100 σημεία ενδιαφέροντος στα Χανιά και έχει συλλεχθεί από την ομάδα του Euclid. Για κάθε σημείο ενδιαφέροντος έχουμε διαθέσιμες τις εξής πληροφορίες:
- Δήμος
- Κατηγορία
- Αντικείμενο
- Περιοχή
- Σημείο ενδιαφέροντος


## poi-twitter
Το dataset points of interest twitter έχει συλλεχθεί από την ομάδα του Euclid. 
Στο αρχικό dataset υπήρχαν 1544 κόμβους του Twitter. 
Διαπιστώσαμε ότι 725 καταχωρήσεις αποτελούσαν αντίγραφα. 
Συνεπώς ο αριθμός των μοναδικών λογαριασμών ήταν 819. 
Ωστόσο, ύστερα από έλεγχο που πραγματοποιήθηκε στης 28/04/2021, 
93 λογαριασμοί δεν υπήρχαν πλέον και 14 λογαριασμοί ήταν προστατευόμενοι. 
Συνεπώς, ο αριθμός των χρήσιμων κόμβων ήταν 712. 
Οι κόμβοι αυτοί έχουν χαρακτηριστεί με 208 διαφορετικές κατηγορίες. 
Για κάθε κόμβο έχουμε τα ακόλουθα χαρακτηριστικά:
- ID
- Twitter Handle
- Category
