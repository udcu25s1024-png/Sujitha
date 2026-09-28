from pathlib import Path
def build_comic_layout(stories,paths):
    if len(stories)!=len(paths): raise ValueError('Every story panel needs an image.')
    return [s.model_copy(update={'image_url':f'/static/panels/{Path(p).name}'}) for s,p in zip(stories,paths)]
