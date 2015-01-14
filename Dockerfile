FROM python:onbuild

# Expose the web-app port
EXPOSE 5000

# Run
CMD ["python3", "climber.py"]
