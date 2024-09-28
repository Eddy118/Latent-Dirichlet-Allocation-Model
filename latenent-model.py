import os
import certifi
import nltk
from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import gensim.corpora as corpora
from gensim.models import LdaModel
from nltk.corpus import stopwords, reuters
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from flask_cors import CORS
import re

# Configure SSL certificate
os.environ['SSL_CERT_FILE'] = certifi.where()

# Download NLTK data files (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('reuters')
nltk.download('wordnet')

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['readIt']
collection = db['documents']

# List of predefined categories
PreferenceListing = [
    "Science Fiction", "Fantasy", "Romance", "Thriller", "Horror", "Historical",
    "Non-Fiction", "Biography", "Self-Help", "Travel", "Adventure", "Cooking",
    "Art", "Poetry", "Comics", "Graphic Novels", "Drama", "Religion", "Philosophy",
    "Science", "Mathematics", "Health", "Fitness", "Technology", "Business",
    "Economics", "Education", "Parenting", "Sports", "Music", "Photography",
    "Gardening", "DIY", "Mystery", "Psychology", "Spirituality", "Environment",
    "Politics", "Law", "Anthropology", "Sociology", "Astronomy", "Programming",
    "Movies", "Television", "Animals", "Pets", "Gaming", "Fashion", "Interior Design",
    "Architecture", "Crafts", "Knitting", "Quilting", "Fishing", "Hiking", "Cycling",
    "Skateboarding", "Snowboarding", "Surfing", "Camping", "Martial Arts", "Dance",
    "Yoga", "Mindfulness", "History of Science", "Foreign Languages", "Linguistics",
    "Mythology", "Folklore", "Urban Studies", "Ethics", "Cultural Studies",
    "Archaeology", "Genealogy", "Equestrian"
]

# Mapping of subcategories to main categories
category_subcategory_mapping = {
    "selling" : "Surfing",
    "diversify" : "Education",
    "scientific" : "Technology",
    "network" : "Technology",
    "silicon" : "Technology",
    "holleb" : "Ethics",
    "san" : "Environment",
    "caremark" : "Environment",
    "stanadyne" : "Environment",
    "combination" : "Mindfulness",
    "offer" : "Education",
    "low" : "Travel",
    "steinberg" : "Mystery",
    "hanover" : "Environment",
    "watt" : "Education",
    "altus" : "Martial Arts",
    "warner": "Camping",
    "cane" : "Education",
    "oilseed": "Business",
    "date" : "Education",
    "ione" : "Education",
    "duffour" : "Education",
    "neptune" : "Education",
    "peerless" : "Martial Arts",
    "transworld" : "Education",
    "gros" : "Education",
    "aluminum" : "Archaeology",
    "day" : "Education",
    "offset" : "Archaeology",
    "gillette" : "Archaeology",
    "workforce" : "Business",
    "cyclops" : "Education",
    "primerica" : "Education",
    "borrower" : "Business",
    "working" : "Fitness",
    "slower" : "Television",
    "related" : "Self-Help",
    "nakasone" : "Self-Help",
    "worker" : "Snowboarding",
    "restart" : "Technology",
    "tobacco" : "Business",
    "ageements" : "Business",
    "ski" : "Snowboarding",
    "estimate" : "Crafts",
    "wk" : "Business",
    "sullivan" : "Business",
    "sale" : "Non-Fiction",
    "warship": "Religion",
    "montagne": "Business",
    "window": "Business",
    "bfi": "Environment",
    "ldp": "Business",
    "kuroda": "Self-Help",
    "sobeys": "Crafts",
    "hold": "Business",
    "howell" : "Biography",
    "fox": "Adventure",
    "boeing" : "Adventure",
    "westcoast": "Adventure",
    "boliden": "Dance",
    "samuel": "Business",
    "pledge": "Business",
    "stock" : "Bussiness",
    "launch" : "Mystery",
    "understands": "Business",
    "shoe": "Business",
    "progas": "Business",
    "impose": "Business",
    "ivory": "Economics",
    "added": "Business",
    "co": "Non-Fiction",
    "turkey": "Business",
    "retaliation": "Business",
    "tlx": "Business",
    "beverage": "Adventure",
    "difference": "Comics",
    "seidman": "Business",
    "ahead": "Business",
    "dirham": "Business",
    "ic": "Business",
    "entregrowth": "Business",
    "northeast": "Historical",
    "ssbb": "Business",
    "fine": "Graphic Novels",
    "exxon": "Art",
    "kuwaiti": "Poetry",
    "yemen": "Architecture",
    "westin": "Architecture",
    "approximately": "Travel",
    "sarcinelli": "Business",
    "guilder": "Cooking",
    "swift": "Business",
    "grumman": "Science",
    "minister": "Business",
    "stratum": "Business",
    "purchased": "Business",
    "imaging": "Business",
    "minstar": "Business",
    "apollo": "Business",
    "tw": "Business",
    "final": "Business",
    "guinness": "Business",
    "super": "Business",
    "cancelled": "Business",
    "datagraph": "Business",
    "rb": "Business",
    "prior": "Business",
    "met": "Business",
    "kilo": "Mathematics",
    "colombo": "Business",
    "liberal": "Science Fiction",
    "bramall": "Skateboarding",
    "ivorian": "Skateboarding",
    "unknown": "Religion",
    "bancorp": "Business",
    "design": "Business",
    "kiena": "Business",
    "vr": "Business",
    "bag": "Business",
    "reason": "Business",
    "june": "Philosophy",
    "mercantile": "Business",
    "far": "Cooking",
    "mmal": "Business",
    "positive": "Business",
    "gelco": "Business",
    "warrant": "Business",
    "bangemann": "Business",
    "stop": "Thriller",
    "wurlitzer": "Drama",
    "public": "Technology",
    "saying": "Parenting",
    "humana": "Business",
    "floating": "Business",
    "myers": "Sports",
    "bryant": "Fantasy",
    "afg": "Business",
    "quaker": "Business",
    "medtec": "Biography",
    "kerr": "Business",
    "breslube": "Business",
    "last": "Business",
    "trader": "Business",
    "tachonics": "Business",
    "refloated": "Health",
    "labelling": "Business",
    "licht": "Adventure",
    "thailand": "Business",
    "kahan": "Horror",
    "hawaiian": "Business",
    "atlantis": "Self-Help",
    "previous": "DIY",
    "yellowknife": "Business",
    "restated": "Travel",
    "semicon": "Business",
    "capitalized": "Spirituality",
    "citizenship": "Business",
    "remaining": "Yoga",
    "previously": "Business",
    "gnp": "Business",
    "bonus": "Business",
    "leutwiler": "Business",
    "asarco": "Business",
    "considering": "Romance",
    "hartmarx": "Business",
    "yr": "Business",
    "increase": "Music",
    "steady": "Business",
    "ajinomoto": "Business",
    "distillate": "Business",
    "west": "Law",
    "lomas": "Business",
    "toshiba": "Business",
    "oecf": "Law",
    "brooklyn": "Pets",
    "castor": "Gaming",
    "common": "Gaming",
    "sony": "Psychology",
    "maryland": "Business",
    "canal": "Business",
    "managing": "Photography",
    "sperry": "Mindfulness",
    "raytheon": "Mindfulness",
    "currency": "Pets",
    "noblee": "Knitting",
    "banker": "Business",
    "secretary": "Mystery",
    "forbes": "Business",
    "gordon": "Business",
    "raytech": "Knitting",
    "mortgage": "Business",
    "reliance": "Business",
    "miti": "Business",
    "european": "Business",
    "liberty": "Business",
    "energas": "Business",
    "sedgwick": "Mystery",
    "brandon": "Business",
    "recovery": "Business",
    "proceeds": "Business",
    "nippon": "Business",
    "agip": "Business",
    "decline": "Politics",
    "dinar": "Business",
    "korea": "Business",
    "destin": "Business",
    "maxicare": "Business",
    "trailways": "Business",
    "advised": "Business",
    "communication": "Business",
    "per": "Business",
    "adam": "Business",
    "reserve": "Gardening",
    "soviet": "Astronomy",
    "ambac": "Business",
    "kwik": "Astronomy",
    "pound": "Business",
    "jardine": "Business",
    "volcker": "Business",
    "agreement": "Anthropology",
    "computerland": "Business",
    "dauster": "Movies",
    "making": "Business",
    "cabinet": "Business",
    "fund": "Anthropology",
    "town": "Programming",
    "dow": "Programming",
    "great": "Business",
    "precision": "Anthropology",
    "gander": "Business",
    "mining": "Business",
    "reebok": "Business",
    "arrow": "Business",
    "coverage": "Business",
    "plant": "Business",
    "interfirst": "Business",
    "dallas": "Business",
    "reject": "Business",
    "tell": "Sociology",
    "ban": "Business",
    "handling": "Business",
    "link": "Business",
    "heidrun": "Business",
    "interest": "Business",
    "science": "Sociology",
    "prince": "Business",
    "kimbark": "Business",
    "haba": "Business",
    "brookehill": "Business",
    "nuclear": "Business",
    "fluor": "Business",
    "mckesson": "Television",
    "motor": "Business",
    "advertising": "Mythology",
    "stockholder": "Business",
    "senator": "Mythology",
    "el": "Business",
    "confidata": "Business",
    "steel": "Business",
    "acquire": "Business",
    "hollis": "Television",
    "awaiting": "Business",
    "close": "Business",
    "life": "Adventure",
    "arsenide": "Business",
    "tin": "Business",
    "heavily": "Business",
    "agriculture": "Business",
    "asked": "Business",
    "real": "Business",
    "krenzler": "Business",
    "fleet": "Business",
    "count": "Business",
    "fidelcor": "Business",
    "bii": "Business",
    "royex": "Business",
    "review": "Business",
    "berkey": "Business",
    "brown": "History of Science",
    "brussels": "Business",
    "westpac": "History of Science",
    "weighs": "Business",
    "ordinary": "Business",
    "strike": "Business",
    "power": "Business",
    "xylene": "Business",
    "mm": "Folklore",
    "deficit": "Business",
    "month": "Business",
    "delay": "Fashion",
    "thomas": "Business",
    "port": "Business",
    "emerged": "Folklore",
    "sao": "Business",
}

# Preprocessing function for document text
def preprocess(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # Tokenize and clean up the text
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalpha() and word not in stop_words]
    return tokens

# Function to process NLTK corpus, extract topics, and store in MongoDB
def process_corpus_and_store_topics():
    document_ids = reuters.fileids()

    for doc_id in document_ids:
        document_text = reuters.raw(doc_id)

        if collection.find_one({"doc_id": doc_id}):
            print(f"Document {doc_id} already exists in the database")
            continue

        processed_doc = preprocess(document_text)

        if not processed_doc:
            print(f"Document {doc_id} resulted in an empty processed document. Skipping.")
            continue

        id2word = corpora.Dictionary([processed_doc])
        corpus = [id2word.doc2bow(processed_doc)]

        if not corpus or len(corpus[0]) == 0:
            print(f"Document {doc_id} resulted in an empty corpus after processing. Skipping.")
            continue

        num_topics = 5

        lda_model = LdaModel(corpus=corpus,
                             id2word=id2word,
                             num_topics=num_topics,
                             random_state=42,
                             update_every=1,
                             chunksize=10,
                             passes=10,
                             alpha='auto',
                             per_word_topics=True)

        topics = lda_model.print_topics(num_words=4)
        topic_list = [{"topic": topic[1]} for topic in topics]

        doc_topics = lda_model.get_document_topics(corpus[0])
        topic_distribution = [{"topic_id": index, "score": float(score)} for index, score in
                              sorted(doc_topics, key=lambda tup: -1 * tup[1])]

        document_data = {
            "doc_id": doc_id,
            "text": document_text,
            "topics": topic_list,
            "topic_distribution": topic_distribution,
            "timestamp": datetime.now()
        }

        collection.insert_one(document_data)
        print(f"Document {doc_id} and topics stored in MongoDB")

# Function to extract actual words from the topic string
def extract_topic_words(extracted_topics):
    topic_words = set()
    topic_pattern = re.compile(r'\*"\s*([^"]+)\s*"')

    for topic in extracted_topics:
        words_found = topic_pattern.findall(topic)
        topic_words.update(words_found)

    return list(topic_words)

# Function to map extracted topics to the predefined categories
def match_topics_to_categories(extracted_topics, requested_categories):
    matched_categories = set()

    # Extract only the words from the topic strings
    topic_words = extract_topic_words(extracted_topics)

    # Get subcategories matching the requested categories
    subcategories = {subcategory for category in requested_categories
                     for subcategory, cat in category_subcategory_mapping.items()
                     if cat.lower() == category.lower()}

    # Match extracted topic words with subcategories
    for word in topic_words:
        if any(subcategory.lower() in word.lower() for subcategory in subcategories):
            matched_categories.add(word)

    return list(matched_categories)

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/documents', methods=['GET'])
def get_documents():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    skip = (page - 1) * page_size

    topics = request.args.get('topics', None)

    if topics:
        requested_topics = topics.split(',')
        query = {"topics.topic": {"$in": requested_topics}}
    else:
        query = {}

    matching_documents = list(collection.find(query, {'_id': 0}).skip(skip).limit(page_size))
    total_documents = collection.count_documents({})
    total_matching_documents = len(matching_documents)

    response = {
        "total_matching_documents": total_matching_documents,
        "documents": matching_documents,
        "recommendedDocuments": matching_documents,
        "page": page,
        "page_size": page_size,
        "total_documents": total_documents,
    }
    return jsonify(response)

@app.route('/documents/match', methods=['POST'])
def match_documents_to_categories():

    requested_categories = request.json.get('categories', [])

    if not requested_categories:
        return jsonify({"error": "No categories provided"}), 400



    # Get all subcategories that match the provided categories
    subcategories = []
    for requested_category in requested_categories:
        subcategories.extend([subcategory for subcategory, category in category_subcategory_mapping.items()
                              if category.lower() == requested_category.lower()])

    if not subcategories:
        return jsonify({"error": "No matching subcategories found"}), 400

    page = int(request.json.get('page', 1))
    page_size = int(request.json.get('page_size', 200))
    skip = (page - 1) * page_size

    # Fetch all documents from the database
    all_documents = list(collection.find({}, {'_id': 0}).skip(skip).limit(page_size))

    document_scores = []
    recommended_documents = []

    # Loop through each document and count the subcategory matches
    for document in all_documents:
        extracted_topics = [topic["topic"] for topic in document.get("topics", [])]
        matched_categories = match_topics_to_categories(extracted_topics, requested_categories)

        matching_subcategories_count = sum(1 for subcategory in subcategories if subcategory in matched_categories)

        if matching_subcategories_count > 0:
            document_scores.append({
                "document": document,
                "matching_subcategories_count": matching_subcategories_count
            })
        else:
            recommended_documents.append({
                "document": document,
                "matching_subcategories_count": matching_subcategories_count
            })

    # Sort documents by number of subcategory matches
    ranked_documents = sorted(document_scores, key=lambda x: x["matching_subcategories_count"], reverse=True)
    matched_documents = [doc["document"] for doc in ranked_documents]

    # unique_matching_items = {item['doc_id']: item for item in matched_documents}.values()
    # unique_recommended_items = {item['doc_id']: item for item in recommended_documents}
    response = {
        "matched_documents": matched_documents,
        "recommended_documents": recommended_documents,
        "total_matched_documents": len(all_documents),
        "page_size": page_size,
    }
    return jsonify(response)

@app.route('/', methods=['GET'])
def status():
    return "ok"

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(process_corpus_and_store_topics, 'interval', hours=12)
scheduler.start()

# Run the Flask app
if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
