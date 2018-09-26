# NYT Corpus Reader

A parser and MongoDB backed store for searching the New York Times
Annotated Corpus (LDC2008T19).

## Usage

To parse an individual NYT Article from file, string, or `ElementTree`:

```
from nyt_parser import NYTArticle

# From file
with open('file.xml', encoding='utf8') as input_file:
    article = NYTArticle.from_file(input_file)

# From string
article = NYTArticle.from_str(string)

# From ElementTree/Element
article = NYTArticle.from_element_tree(element)


# To convert into a dictionary
article_dict = article.as_dict()
```

In addition to processing an individual file, this package can be used to ingest the entire corpus into MongoDB. To do so, use the script `ingest_nyt.py`, providing a list of compressed files from the original dataset to ingest.

The articles are ingested into the collection `nyt.articles` and indexed by document id, general descriptors, and types of material. Once ingested, standard MongoDB client calls can be used to search and retrieve the articles.

## Installation

To install requirements, run `pip install -r requirements.txt`. This package is not yet pip-installable but will be in the near future.


## Other NYT Annotated Corpus software

* https://github.com/grimpil/nyt-summ
* https://github.com/notnews/nytimes-corpus-extractor
* https://github.com/thedansimonson/nyt_corpus_reader

## Acknowledgments

This package was developed at the University of Southern California Information Sciences institute under the MATERIAL program.
