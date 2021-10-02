import io
import pytest
from training import training_phase
from elasticity_training import TrainingElasticity

sessions_quantity = [20, 25]


@pytest.mark.parametrize('session_quantity', sessions_quantity)
def test_training_phase(monkeypatch, session_quantity):
    monkeypatch.setattr('sys.stdin', io.StringIO('1\n1\n'))

    TrainingElasticity.rewrite_data_ingestion_config(session_quantity)

    training_phase()

    assert True


@pytest.fixture(scope="session", autouse=True)
def generate_final_dataframe(request):
    elasticity = TrainingElasticity(sessions_quantity)
    elasticity.clean_csv_file()

    def finalizer_function():
        elasticity.generate_plots()

    request.addfinalizer(finalizer_function)
