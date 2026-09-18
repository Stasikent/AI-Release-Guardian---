from app.rag.chunking import chunk_text
def test_chunking_is_bounded_and_overlapping():
    text=" ".join(f"token{i}" for i in range(300))
    chunks=chunk_text(text,max_chars=200,overlap_chars=30)
    assert len(chunks)>2
    assert all(len(c.text)<=200 for c in chunks)
    assert [c.index for c in chunks]==list(range(len(chunks)))
