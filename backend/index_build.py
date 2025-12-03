# backend/index_build.py
from .rag import RAGIndex, load_seed_docs


def main():
    docs = load_seed_docs('data/seed_docs')
    rag = RAGIndex()
    rag.build_from_docs(docs)
    print('Index built with', len(docs), 'docs')


if __name__ == '__main__':
    main()
