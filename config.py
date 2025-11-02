"""
Configuration for medical curriculum structure
"""
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    exit(1)

CONFIG = {
    "data_dir": "data",
    "database_file": "quiz_bot.db",
    "max_questions_per_quiz": 100,
    "time_between_questions": 1,
}

# Medical Curriculum Structure
NAVIGATION_STRUCTURE = {
    "year_1": {
        "display_name": "Year 1",
        "terms": {
            "term_1": {
                "display_name": "Term 1", 
                "blocks": {
                    "block_1": {
                        "display_name": "Block 1",
                        "subjects": {
                            "anatomy": {
                                "display_name": "📊 Anatomy",
                                "categories": {
                                    "general": {
                                        "display_name": "General Anatomy",
                                        "subtopics": {
                                            "Introduction to Anatomy.csv": "Introduction to Anatomy",
                                            "Skin and Fascia.csv": "Skin and Fascia",
                                            "Muscles.csv": "Muscles",
                                            "Bones and Cartilages.csv": "Bones and Cartilages",
                                            "Joints.csv": "Joints",
                                            "Skeletal system.csv": "Skeletal system",
                                            "Digestive system.csv": "Digestive system",
                                            "Respiratory system.csv": "Respiratory system",
                                            "Nervous system.csv": "Nervous system",
                                            "Cardiovascular system & Lymphatic systems.csv": "Cardiovascular & Lymphatic systems",
                                            "Urinary system.csv": "Urinary system",
                                            "Genital system.csv": "Genital system",
                                            "Human Chromosomes.csv": "Human Chromosomes",
                                            "Spermatogenesis.csv": "Spermatogenesis",
                                            "Oogenesis.csv": "Oogenesis",
                                            "Ovarian cycle - Ovulation.csv": "Ovarian cycle - Ovulation",
                                            "Fertilization.csv": "Fertilization",
                                            "Cleavage - Blastocyst formation.csv": "Cleavage - Blastocyst formation",
                                            "Uterus at time of implantation.csv": "Uterus at time of implantation",
                                            "2nd week of development.csv": "2nd week of development",
                                            "3rd Week of Development Gastrulation and Notochord formation.csv": "3rd Week - Gastrulation",
                                            "Further development of the Trophoblast.csv": "Trophoblast development",
                                            "3rd to 8th Week (The Embryonic Period).csv": "3rd to 8th Week - Embryonic Period",
                                            "Derivatives of the Ectodermal Germ Layer.csv": "Ectodermal Derivatives",
                                            "Derivatives of the Mesodermal Germ Layer.csv": "Mesodermal Derivatives",
                                            "Derivatives of the Endodermal Germ Layer.csv": "Endodermal Derivatives",
                                            "External appearance during 2nd month of pregnancy.csv": "2nd Month - External Appearance",
                                            "3rd Month to birth - Fetal Monthly changes - Time of birth.csv": "3rd Month to Birth",
                                            "Placenta.csv": "Placenta",
                                            "Umbilical Cord.csv": "Umbilical Cord",
                                            "Amnion, amniotic fluid.csv": "Amnion & Amniotic Fluid",
                                            "Twins.csv": "Twins"
                                        }
                                    },
                                    "Midterm": {
                                        "display_name": "Midterm Exams",
                                        "subtopics": {
                                            "Midterm Questions_1.csv": "Midterm Questions 1",
                                            "Midterm Questions_2.csv": "Midterm Questions 2",
                                            "Midterm Questions_3.csv": "Midterm Questions 3"
                                        }
                                    },
                                    "Final": {
                                        "display_name": "Final Exams", 
                                        "subtopics": {
                                            "Final Questions_1.csv": "Final Questions 1",
                                            "Final Questions_2.csv": "Final Questions 2",
                                            "Final Questions_3.csv": "Final Questions 3"
                                        }
                                    },
                                    "Formative": {
                                        "display_name": "Formative Assessments",
                                        "subtopics": {
                                            "Formative_1.csv": "Formative 1",
                                            "Formative_2.csv": "Formative 2", 
                                            "Formative_3.csv": "Formative 3",
                                            "Formative_4.csv": "Formative 4",
                                            "Formative_5.csv": "Formative 5"
                                        }
                                    }
                                }
                            },
                            "histology": {
                                "display_name": "🔬 Histology",
                                "categories": {
                                    "general": {
                                        "display_name": "General Histology", 
                                        "subtopics": {
                                            "Paraffin technique.csv": "Paraffin Technique",
                                            "Types of microscopes.csv": "Types of Microscopes",
                                            "Cell & tissue culture.csv": "Cell & Tissue Culture",
                                            "Membranous organelles.csv": "Membranous Organelles",
                                            "Non membranous organelles.csv": "Non-Membranous Organelles",
                                            "Inclusions.csv": "Inclusions",
                                            "Nucleus.csv": "Nucleus",
                                            "Cell cycle and Cell death.csv": "Cell Cycle & Cell Death",
                                            "Epithelial tissues.csv": "Epithelial Tissues",
                                            "Connective tissues.csv": "Connective Tissues", 
                                            "Cartilage.csv": "Cartilage",
                                            "Bone.csv": "Bone"
                                        }
                                    },
                                    "Midterm": {
                                        "display_name": "Midterm Exams",
                                        "subtopics": {
                                            "Midterm Questions_1.csv": "Midterm Questions 1",
                                            "Midterm Questions_2.csv": "Midterm Questions 2",
                                            "Midterm Questions_3.csv": "Midterm Questions 3"
                                        }
                                    },
                                    "Final": {
                                        "display_name": "Final Exams",
                                        "subtopics": {
                                            "Final Questions_1.csv": "Final Questions 1",
                                            "Final Questions_2.csv": "Final Questions 2",
                                            "Final Questions_3.csv": "Final Questions 3"
                                        }
                                    },
                                    "Formative": {
                                        "display_name": "Formative Assessments",
                                        "subtopics": {
                                            "Formative_1.csv": "Formative 1",
                                            "Formative_2.csv": "Formative 2",
                                            "Formative_3.csv": "Formative 3",
                                            "Formative_4.csv": "Formative 4",
                                            "Formative_5.csv": "Formative 5"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}