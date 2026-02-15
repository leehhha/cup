from setuptools import setup, find_packages

setup(
    name="gift-reminder",
    version="1.0.0",
    description="A personal gift reminder and suggestion app for your partner",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "customtkinter>=5.2.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gift-reminder=gift_reminder.app:main",
        ],
    },
)
