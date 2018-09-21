#! /usr/bin/env python
"""
Ingest a list of .tar files into the MongoDB store.
"""

import argparse
import multiprocessing
import tarfile
from typing import Iterable, Dict, Any

from pymongo import MongoClient
from pymongo.collection import Collection

from nytcorpusreader import NYTArticle

_XML_SUFFIX = '.xml'
_BULK_INSERT_SIZE = 1000


def get_documents(tar_path: str) -> Iterable[NYTArticle]:
    with tarfile.open(tar_path, 'r:*') as tar:
        for inner_file in tar:
            filename = inner_file.name
            # Skip everything but the articles
            if not filename.endswith(_XML_SUFFIX):
                continue

            content = tar.extractfile(inner_file).read().decode('utf8')
            article = NYTArticle.from_str(content)
            yield article


def process_path(tar_path: str) -> None:
    with _get_client() as client:
        article_collection = _get_collection(client)
        articles = []
        for article in get_documents(tar_path):
            if article:
                articles.append(article)
            # Bulk insert for speed
            if len(articles) >= _BULK_INSERT_SIZE:
                article_collection.insert_many(_articles_to_dicts(articles))
                articles = []

        # Insert leftovers
        article_collection.insert_many(_articles_to_dicts(articles))


def _get_client() -> MongoClient:
    return MongoClient()


def _get_collection(client: MongoClient) -> Collection:
    # TODO: Make collection name configurable
    return client.nyt.articles


def _articles_to_dicts(articles: Iterable[NYTArticle]) -> Iterable[Dict[Any, Any]]:
    for article in articles:
        yield article.as_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('list', type=argparse.FileType('r', encoding='utf8'),
                        help='A file containing a list of tar files to ingest')
    parser.add_argument('nworkers', type=int, default=1, nargs='?',
                        help='Number of workers to use for ingest')
    args = parser.parse_args()
    nworkers = args.nworkers

    # Parse file list
    files = [line.strip() for line in args.list]
    args.list.close()
    if not files:
        raise ValueError('No files in input file list')

    # Clear anything in there
    with _get_client() as client:
        article_collection = _get_collection(client)
        # TODO: Make dropping opt-in
        article_collection.drop()

    print('Ingesting documents using {} workers'.format(nworkers))
    # Process in parallel
    pool = multiprocessing.Pool(nworkers)
    for filename in files:
        # TODO: Check for errors
        pool.apply_async(process_path, (filename,))
    pool.close()
    pool.join()

    print('Creating indices')
    with _get_client() as client:
        article_collection = _get_collection(client)
        article_collection.create_index('docid', unique=True)
        article_collection.create_index('general_descriptors')
        article_collection.create_index('types_of_material')


if __name__ == '__main__':
    main()
