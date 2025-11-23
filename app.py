from flask import Flask, request, render_template
import joblib
import re

app = Flask(__name__)
model = joblib.load("phishing_model.pkl")

# Feature extraction (must match training script!)
def has_ip(url):
    ip_pattern = r"(https?:\/\/)?(\d{1,3}\.){3}\d{1,3}"
    return 1 if re.search(ip_pattern, url) else 0

def count_dots(url):
    return url.count(".")

def has_at(url):
    return 1 if "@" in url else 0

def uses_https(url):
    return 1 if url.startswith("https") else 0

def uses_shortener(url):
    shorteners = ["bit.ly", "tinyurl", "goo.gl", "ow.ly", "is.gd", "buff.ly", "adf.ly"]
    return 1 if any(s in url for s in shorteners) else 0

def extract_features(url):
    return [
        len(url),
        count_dots(url),
        has_at(url),
        has_ip(url),
        uses_https(url),
        uses_shortener(url)
    ]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        url = request.form.get("url", "").strip()
        if not url:
            return render_template("index.html", error="Please enter a URL")
        
        features = extract_features(url)
        prediction = model.predict([features])[0]
        result = "⚠️ Phishing Website" if prediction == 1 else "✅ Legitimate Website"
        return render_template("index.html", prediction=result, url=url)
    except Exception as e:
        return render_template("index.html", error=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

