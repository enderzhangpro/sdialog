from sdialog import Dialog
from sdialog.personas import Agent
from sdialog.generators import LLMDialogOutput, Turn
from sdialog.personas import Persona, ExtendedPersona, Doctor, Patient, PersonaMetadata, MinimalPatient, MinimalDoctor

MODEL = "smollm:135m"
example_dialog = Dialog(turns=[Turn(speaker="A", text="This is an example!"), Turn(speaker="B", text="Hi!")])


# Patch LLM call
class DummyLLM:
    seed = 0
    num_predict = 1

    def __init__(self, *a, **kw):
        pass

    def invoke(self, memory):
        return type(
            "Msg", (),
            {"content": LLMDialogOutput(
                dialog=[Turn(speaker="A", text="Hi")]).model_dump_json()}
        )()

    def __str__(self):
        return "dummy"


def test_persona_description_and_json():
    p = Persona(name="Test", role="tester")
    desc = p.description()
    assert "Test" in desc
    js = p.json()
    assert isinstance(js, dict)
    js_str = p.json(string=True)
    assert isinstance(js_str, str)


def test_persona_fields():
    p = Persona(name="Alice", role="barista", background="Cafe")
    assert p.name == "Alice"
    assert p.role == "barista"
    assert p.background == "Cafe"


def test_persona_agent_init(monkeypatch):
    persona = Persona(name="Alice")
    agent = Agent(persona=persona, name="Alice", model=DummyLLM())
    assert agent.get_name() == "Alice"
    assert "role" in agent.prompt().lower()
    agent.set_first_utterances("Hi!")
    assert agent.first_utterances == "Hi!"
    agent.clear_orchestrators()
    agent.reset(seed=42)


def test_persona_and_json():
    persona = Persona(name="Alice", role="barista", background="Works at a cafe")
    desc = persona.description()
    assert "Alice" in desc
    js = persona.json()
    assert isinstance(js, dict)
    js_str = persona.json(string=True)
    assert isinstance(js_str, str)
    assert "Alice" in js_str


def test_persona_agent_init_and_prompt():
    persona = Persona(name="Alice", role="barista")
    agent = Agent(persona, "Alice", MODEL)
    assert agent.get_name() == "Alice"
    prompt = agent.prompt()
    assert "role" in prompt.lower()


def test_persona_agent_dialog_with():
    persona1 = Persona(name="A")
    persona2 = Persona(name="B")
    agent1 = Agent(persona=persona1, name="A", model=DummyLLM())
    agent2 = Agent(persona2, "B", DummyLLM())
    dialog = agent1.dialog_with(agent2, max_turns=4, keep_bar=False)
    assert isinstance(dialog, Dialog)
    assert len(dialog.turns) > 0
    assert "A" in dialog.personas
    assert "B" in dialog.personas


def test_agent_postprocessing_fn():
    persona1 = Persona(name="A")
    persona2 = Persona(name="B")
    agent1 = Agent(persona=persona1, name="A", model=DummyLLM())
    agent2 = Agent(persona2, "B", DummyLLM(), postprocess_fn=lambda x: x.upper())
    dialog = agent1.dialog_with(agent2, max_turns=4, keep_bar=False)
    assert dialog.turns[1].text.isupper(), "Postprocessing function did not apply correctly."
    assert not dialog.turns[0].text.isupper(), "Postprocessing function should not have effect."


def test_extended_persona_fields_and_description():
    p = ExtendedPersona(
        name="Bob",
        age=40,
        race="Asian",
        gender="male",
        language="English",
        weight="70kg",
        height=175.0,
        occupation="Engineer",
        education="PhD",
        socioeconomic_status="middle",
        interests="AI, robotics",
        hobbies="chess",
        politeness="high",
        forgetfulness="low",
        attentiveness="high",
        communication_style="direct",
        empathy_level="medium",
        political_views="moderate",
        religious_beliefs="agnostic"
    )
    desc = p.description()
    assert "Bob" in desc
    assert "Engineer" in desc
    js = p.json()
    assert isinstance(js, dict)
    assert js["name"] == "Bob"
    assert js["occupation"] == "Engineer"


def test_patient_fields_and_description():
    p = Patient(
        name="Jane",
        age=30,
        symptoms="cough, fever",
        vital_signs="BP 120/80",
        health_literacy="high",
        medical_conditions="asthma",
        medications="inhaler",
        allergies="penicillin",
        family_history="diabetes"
    )
    desc = p.description()
    assert "Jane" in desc
    assert "cough" in desc
    js = p.json()
    assert isinstance(js, dict)
    assert js["symptoms"] == "cough, fever"
    assert js["medical_conditions"] == "asthma"


def test_doctor_fields_and_description():
    d = Doctor(
        name="Dr. Smith",
        age=50,
        specialty="Cardiology",
        years_of_experience=25,
        certifications="Board Certified",
        work_experience="Hospital A, Hospital B"
    )
    desc = d.description()
    assert "Dr. Smith" in desc
    assert "Cardiology" in desc
    js = d.json()
    assert isinstance(js, dict)
    assert js["specialty"] == "Cardiology"
    assert js["years_of_experience"] == 25


def test_MinimalPatient_fields_and_description():
    p = MinimalPatient(
        name="John",
        age=35,
        race="Hispanic",
        gender="male",
        language="Spanish",
        forgetfulness="medium",
        formality="low",
        hurriedness="high",
        openness="medium",
        height=180,
        weight=75,
        occupation="Engineer",
        reason_for_visit="Routine checkup",
        medical_history="No major illnesses",
        medical_conditions="None",
        medications_current="None",
        allergies="None",
        family_history="No significant history",
        marital_status="single",
        insurance="private"
    )
    desc = p.description()
    assert "John" in desc
    assert "Routine checkup" in desc
    assert "Hispanic" in desc
    assert "male" in desc
    assert "Spanish" in desc
    assert "Engineer" in desc
    js = p.json()
    assert isinstance(js, dict)
    assert js["name"] == "John"
    assert js["age"] == 35
    assert js["race"] == "Hispanic"
    assert js["gender"] == "male"
    assert js["language"] == "Spanish"
    assert js["forgetfulness"] == "medium"
    assert js["formality"] == "low"
    assert js["hurriedness"] == "high"
    assert js["openness"] == "medium"
    assert js["height"] == 180
    assert js["weight"] == 75
    assert js["occupation"] == "Engineer"
    assert js["reason_for_visit"] == "Routine checkup"
    assert js["medical_history"] == "No major illnesses"
    assert js["medical_conditions"] == "None"
    assert js["medications_current"] == "None"
    assert js["allergies"] == "None"
    assert js["family_history"] == "No significant history"


def test_MinimalDoctor_fields_and_description():
    d = MinimalDoctor(
        name="Dr. Jane",
        age=45,
        speciality="Pediatrics",
        years_of_experience=20,
        race="Caucasian",
        gender="female",
        language="English",
        forgetfulness="low",
        formality="high",
        hurriedness="medium",
        openness="high"
    )
    desc = d.description()
    print(desc)
    assert "Dr. Jane" in desc
    assert "Pediatrics" in desc
    js = d.json()
    assert isinstance(js, dict)
    assert js["speciality"] == "Pediatrics"
    assert js["years_of_experience"] == 20
    assert js["race"] == "Caucasian"
    assert js["gender"] == "female"
    assert js["language"] == "English"
    assert js["forgetfulness"] == "low"
    assert js["formality"] == "high"
    assert js["hurriedness"] == "medium"
    assert js["openness"] == "high"


def test_persona_to_file_and_from_file(tmp_path):
    """
    Test saving and loading a Persona (BasePersona subclass) to/from file, including metadata.
    """
    persona = Persona(name="Alice", role="barista", background="Works at a cafe")
    file_path = tmp_path / "persona.json"
    persona.to_file(str(file_path))
    loaded = Persona.from_file(str(file_path))
    assert isinstance(loaded, Persona)
    assert loaded.name == "Alice"
    assert loaded.role == "barista"
    assert loaded.background == "Works at a cafe"
    assert hasattr(loaded, "_metadata")
    assert loaded._metadata is not None
    assert loaded._metadata.className == Persona.__name__


def test_extended_persona_to_file_and_from_file(tmp_path):
    """
    Test saving and loading an ExtendedPersona (BasePersona subclass) to/from file, including metadata.
    """
    p = ExtendedPersona(
        name="Bob",
        age=40,
        race="Asian",
        gender="male",
        language="English",
        weight="70kg",
        height=175.0,
        occupation="Engineer",
        education="PhD",
        socioeconomic_status="middle",
        interests="AI, robotics",
        hobbies="chess",
        politeness="high",
        forgetfulness="low",
        attentiveness="high",
        communication_style="direct",
        empathy_level="medium",
        political_views="moderate",
        religious_beliefs="agnostic"
    )
    file_path = tmp_path / "extended_persona.json"
    p.to_file(str(file_path))
    loaded = ExtendedPersona.from_file(str(file_path))
    assert isinstance(loaded, ExtendedPersona)
    assert loaded.name == "Bob"
    assert loaded.occupation == "Engineer"
    assert loaded._metadata is not None
    assert loaded._metadata.className == ExtendedPersona.__name__


def test_persona_clone():
    """
    Test the .clone() method for Persona and ExtendedPersona, ensuring deep copy and metadata preservation.
    """
    persona = Persona(name="Alice", role="barista", background="Works at a cafe")
    clone = persona.clone()
    assert isinstance(clone, Persona)
    assert clone is not persona
    assert clone.name == persona.name
    assert clone.role == persona.role
    assert clone.background == persona.background
    assert hasattr(clone, "_metadata")
    assert clone._metadata is not None
    assert clone._metadata.className == Persona.__name__

    # ExtendedPersona
    p = ExtendedPersona(
        name="Bob",
        age=40,
        occupation="Engineer"
    )
    p._metadata = None
    clone2 = p.clone()
    assert isinstance(clone2, ExtendedPersona)
    assert clone2 is not p
    assert clone2.name == p.name
    assert clone2.occupation == p.occupation
    assert clone2._metadata is not None
    assert clone2._metadata.className == ExtendedPersona.__name__


def test_persona_clone_parent_id():
    """
    Test that .clone() sets the clone's _metadata.parentId to the original's _metadata.id.
    """
    persona = Persona(name="Alice", role="barista")
    persona._metadata = PersonaMetadata(id=123)
    clone = persona.clone()
    assert clone._metadata is not None
    assert clone._metadata.parentId == 123


def test_persona_clone_with_changes():
    """
    Test that .clone() can produce a modified clone when attributes are changed after cloning.
    """
    persona = Persona(name="Alice", role="barista", background="Works at a cafe")
    clone = persona.clone(role="manager")
    assert clone.role == "manager"
    assert persona.name == clone.name


def test_agent_example_dialogs():
    persona = Persona(name="Alice")
    agent = Agent(persona=persona, name="Alice", model=DummyLLM(), example_dialogs=[example_dialog])
    assert example_dialog.turns[0].text in agent.memory[0].content
