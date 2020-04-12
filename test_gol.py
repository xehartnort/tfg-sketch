from libs.GoL import GameOfLife

mainPath = './patterns/test_patterns/'
imgPath = './patterns/test_images/'

def test_block():
    life = GameOfLife(lifeFromFile = mainPath+'block.rle', prob=1)
    im = life.draw(30)
    im.save(imgPath+'block_rle.png', "PNG")
    lifeEvo = GameOfLife(lifeFromFile = mainPath+'block_evo.rle', prob=1)
    im = lifeEvo.draw(30)
    im.save(imgPath+'block_evo_rle.png', "PNG")
    
    assert life.count() == 4
    assert life.count() == lifeEvo.count()
    assert life.area() == 4
    assert life.area() == lifeEvo.area()
    assert len(life.clusters()) == len(lifeEvo.clusters())

    life.run()
    im = life.draw(30)
    im.save(imgPath+'block_run_rle.png', "PNG")

def test_blinker():
    life = GameOfLife(lifeFromFile = mainPath+'blinker.rle', prob=1)
    im = life.draw(30)
    im.save(imgPath+'blinker_rle.png', "PNG")
    lifeEvo = GameOfLife(lifeFromFile = mainPath+'blinker_evo.rle', prob=1)
    im = lifeEvo.draw(30)
    im.save(imgPath+'blinker_evo_rle.png', "PNG")

    assert life.count() == 3
    assert life.count() == lifeEvo.count()
    assert life.area() == 3
    assert life.area() == lifeEvo.area()
    assert len(life.clusters()) == len(lifeEvo.clusters())

    life.run()
    im = life.draw(30)
    im.save(imgPath+'blinker_run_rle.png', "PNG")

def test_glider():
    life = GameOfLife(lifeFromFile = mainPath+'glider.rle', prob=1)
    im = life.draw(30)
    im.save(imgPath+'glider_rle.png', "PNG")
    lifeEvo = GameOfLife(lifeFromFile = mainPath+'glider_evo.rle', prob=1)
    im = lifeEvo.draw(30)
    im.save(imgPath+'glider_evo_rle.png', "PNG")

    assert life.count() == 5
    assert life.count() == lifeEvo.count()
    assert life.area() == 9
    assert life.area() == lifeEvo.area()
    assert len(life.clusters()) == len(lifeEvo.clusters())

    life.run()
    im = life.draw(30)
    im.save(imgPath+'glider_run_rle.png', "PNG")

