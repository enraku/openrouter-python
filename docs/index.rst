.. OpenRouter Python Client documentation master file, created by
   sphinx-quickstart on Mon Jul 14 01:34:19 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OpenRouter Python Client
========================

A Python client library for the OpenRouter API, providing easy access to multiple AI models.

🦈 Features
-----------

* **Simple API client** for OpenRouter services
* **Chat completion** with various AI models
* **Account balance** and credit monitoring
* **Model information** retrieval
* **Type hints** and full **Pydantic** validation
* **Comprehensive error handling**

Quick Start
-----------

.. code-block:: python

   from openrouter_py import OpenRouterClient

   # Initialize client
   client = OpenRouterClient(api_key="your-api-key")

   # Simple completion
   response = client.simple_completion(
       "Hello, how are you?",
       model="anthropic/claude-3.5-sonnet"
   )
   print(response)

   # Check balance
   balance = client.get_balance()
   print(f"Remaining credits: ${balance.balance:.4f}")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

