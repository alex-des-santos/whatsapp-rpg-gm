// frontend/js/evolution-client.js
class EvolutionClient {
  constructor(apiUrl) {
    this.baseUrl = apiUrl;
  }

  async sendMessage(instance, message) {
    const response = await fetch(`${this.baseUrl}/message/send`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        instanceName: instance,
        message: message
      })
    });
    return response.json();
  }
}
