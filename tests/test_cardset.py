import os
import pytest
import forecastcards

fc_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

ex_data = os.path.join(os.path.join(fc_path,'forecastcards'),'examples')

gh_data = {'username':'e-lo','repository':'forecastcards','branch':'master'}

schema_locs = { 'poi':'https://raw.github.com/e-lo/forecastcards/master/spec/en/poi-schema.json',
                "scenario": "https://raw.github.com/e-lo/forecastcards/master/spec/en/scenario-schema.json",
                "project": "https://raw.github.com/e-lo/forecastcards/master/spec/en/project-schema.json",
                "observations": "https://raw.github.com/e-lo/forecastcards/master/spec/en/observations-schema.json",
                "forecast": "https://raw.github.com/e-lo/forecastcards/master/spec/en/forecast-schema.json",
}
@pytest.mark.master
@pytest.mark.basic
def test_local_cardset():
    #forecastcards.Cardset(data_loc = ex_data)
    forecastcards.Cardset()

@pytest.mark.master
@pytest.mark.basic
def test_github_cardset():
    forecastcards.Cardset(data_loc = gh_data)

if __name__ == '__main__':

    print ("test default")
    test_local_cardset()
    print ("test github")
    test_github_cardset()
