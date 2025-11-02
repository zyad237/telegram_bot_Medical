"""
Configuration for medical curriculum structure with numbered CSV files
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
                                            "01_Introduction to Anatomy.csv": "1. Introduction to Anatomy",
                                            "02_Skin and Fascia.csv": "2. Skin and Fascia",
                                            "03_Muscles.csv": "3. Muscles",
                                            "04_Bones and Cartilages.csv": "4. Bones and Cartilages",
                                            "05_Joints.csv": "5. Joints",
                                            "06_Skeletal system.csv": "6. Skeletal System",
                                            "07_Digestive system.csv": "7. Digestive System",
                                            "08_Respiratory system.csv": "8. Respiratory System",
                                            "09_Nervous system.csv": "9. Nervous System",
                                            "10_Cardiovascular system & Lymphatic systems.csv": "10. Cardiovascular & Lymphatic",
                                            "11_Urinary system.csv": "11. Urinary System",
                                            "12_Genital system.csv": "12. Genital System",
                                            "13_Human Chromosomes.csv": "13. Human Chromosomes",
                                            "14_Spermatogenesis.csv": "14. Spermatogenesis",
                                            "15_Oogenesis.csv": "15. Oogenesis",
                                            "16_Ovarian cycle - Ovulation.csv": "16. Ovarian Cycle",
                                            "17_Fertilization.csv": "17. Fertilization",
                                            "18_Cleavage - Blastocyst formation.csv": "18. Cleavage & Blastocyst",
                                            "19_Uterus at time of implantation.csv": "19. Uterus at Implantation",
                                            "20_2nd week of development.csv": "20. 2nd Week Development",
                                            "21_3rd Week of Development Gastrulation and Notochord formation.csv": "21. 3rd Week - Gastrulation",
                                            "22_Further development of the Trophoblast.csv": "22. Trophoblast Development",
                                            "23_3rd to 8th Week (The Embryonic Period).csv": "23. Embryonic Period",
                                            "24_Derivatives of the Ectodermal Germ Layer.csv": "24. Ectodermal Derivatives",
                                            "25_Derivatives of the Mesodermal Germ Layer.csv": "25. Mesodermal Derivatives",
                                            "26_Derivatives of the Endodermal Germ Layer.csv": "26. Endodermal Derivatives",
                                            "27_External appearance during 2nd month of pregnancy.csv": "27. 2nd Month Appearance",
                                            "28_3rd Month to birth - Fetal Monthly changes - Time of birth.csv": "28. 3rd Month to Birth",
                                            "29_Placenta.csv": "29. Placenta",
                                            "30_Umbilical Cord.csv": "30. Umbilical Cord",
                                            "31_Amnion, amniotic fluid.csv": "31. Amnion & Fluid",
                                            "32_Twins.csv": "32. Twins"
                                        }
                                    },
                                    "Midterm": {
                                        "display_name": "📝 Midterm Exams",
                                        "subtopics": {
                                            "01_Midterm Questions.csv": "Midterm 1",
                                            "02_Midterm Questions.csv": "Midterm 2",
                                            "03_Midterm Questions.csv": "Midterm 3"
                                        }
                                    },
                                    "Final": {
                                        "display_name": "🎯 Final Exams", 
                                        "subtopics": {
                                            "01_Final Questions.csv": "Final 1",
                                            "02_Final Questions.csv": "Final 2",
                                            "03_Final Questions.csv": "Final 3"
                                        }
                                    },
                                    "Formative": {
                                        "display_name": "📚 Formative Assessments",
                                        "subtopics": {
                                            "01_Formative.csv": "Formative 1",
                                            "02_Formative.csv": "Formative 2", 
                                            "03_Formative.csv": "Formative 3",
                                            "04_Formative.csv": "Formative 4",
                                            "05_Formative.csv": "Formative 5"
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
                                            "01_Paraffin technique.csv": "1. Paraffin Technique",
                                            "02_Types of microscopes.csv": "2. Types of Microscopes",
                                            "03_Cell & tissue culture.csv": "3. Cell & Tissue Culture",
                                            "04_Membranous organelles.csv": "4. Membranous Organelles",
                                            "05_Non membranous organelles.csv": "5. Non-Membranous Organelles",
                                            "06_Inclusions.csv": "6. Inclusions",
                                            "07_Nucleus.csv": "7. Nucleus",
                                            "08_Cell cycle and Cell death.csv": "8. Cell Cycle & Death",
                                            "09_Epithelial tissues.csv": "9. Epithelial Tissues",
                                            "10_Connective tissues.csv": "10. Connective Tissues", 
                                            "11_Cartilage.csv": "11. Cartilage",
                                            "12_Bone.csv": "12. Bone"
                                        }
                                    },
                                    "Midterm": {
                                        "display_name": "📝 Midterm Exams",
                                        "subtopics": {
                                            "01_Midterm Questions.csv": "Midterm 1",
                                            "02_Midterm Questions.csv": "Midterm 2",
                                            "03_Midterm Questions.csv": "Midterm 3"
                                        }
                                    },
                                    "Final": {
                                        "display_name": "🎯 Final Exams",
                                        "subtopics": {
                                            "01_Final Questions.csv": "Final 1",
                                            "02_Final Questions.csv": "Final 2",
                                            "03_Final Questions.csv": "Final 3"
                                        }
                                    },
                                    "Formative": {
                                        "display_name": "📚 Formative Assessments",
                                        "subtopics": {
                                            "01_Formative.csv": "Formative 1",
                                            "02_Formative.csv": "Formative 2",
                                            "03_Formative.csv": "Formative 3",
                                            "04_Formative.csv": "Formative 4",
                                            "05_Formative.csv": "Formative 5"
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