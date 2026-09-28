from app.models import PromptRequest
def test_strip():
 p=PromptRequest(story_prompt='  fox  ',character_name=' Luna ',setting='Forest',tone='Funny',art_style='Comic'); assert p.story_prompt=='fox' and p.character_name=='Luna'
