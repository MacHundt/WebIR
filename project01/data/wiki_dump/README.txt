** ADD the downloaded and extracted wiki_dump files in this folder.

** RUN edit_extractor.py **
this will create pickle files for every page in the ../data/pickle/ folder

** RUN corpus_creator.py **
to create a training corpus for every found country in ../data/countries/

** or RUN test_set_creator.py **
to create a test set for every found country in ../data/test_pickles/
it will read files from ../data/pickles .. create a corpus for every found country in ../data/countries/test ..
from these country data it will create test pickles (same amount of revisions, same size) for every country.

** RUN writing_style_analyzer.py **
loads the training corpus and trains a model

** RUN test_writing_style_analyzer.py **
to evaluate the model with the test corpus