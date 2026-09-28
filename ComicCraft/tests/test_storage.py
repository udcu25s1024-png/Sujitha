from app.services.storage import safe_filename
def test_safe(): assert safe_filename('../../hello world.pdf')=='hello_world.pdf'
