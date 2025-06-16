# =========================================================================
#                 Dockerfile for the Streamlit States App
# =========================================================================

# 1. BASE IMAGE
# -------------------------------------------------------------------------
# Start from a slim, official Python image for a small final image size.
FROM python:3.13-slim

# 2. SET UP THE ENVIRONMENT
# -------------------------------------------------------------------------
# Set the working directory inside the container.
WORKDIR /app

# 3. INSTALL PYTHON DEPENDENCIES
# -------------------------------------------------------------------------
# Copy the requirements file first to leverage Docker's layer caching. This
# makes future builds much faster if your dependencies don't change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. COPY APPLICATION CODE
# -------------------------------------------------------------------------
# With dependencies installed, copy your Streamlit app code into the container.
COPY app.py .

# 5. EXPOSE PORT
# -------------------------------------------------------------------------
# Expose the default port that Streamlit runs on.
EXPOSE 8501

# 6. DEFINE THE RUN COMMAND
# -------------------------------------------------------------------------
# The command to execute when the container starts. This tells Streamlit
# to run your app and listen for traffic on all network interfaces.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
