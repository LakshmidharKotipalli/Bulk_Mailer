import React, { useState } from "react";
import axios from "axios";

function App() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    smtpServer: "smtp.gmail.com",
    smtpPort: 587,
    subject: "",
    body: "",
    file: null,
  });

  const [status, setStatus] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      file: e.target.files[0],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("Sending...");

    const data = new FormData();
    data.append("email", formData.email);
    data.append("password", formData.password);
    data.append("smtp_server", formData.smtpServer);
    data.append("smtp_port", formData.smtpPort);
    data.append("subject", formData.subject);
    data.append("body", formData.body);
    data.append("file", formData.file);

    try {
      const res = await axios.post("https://your-backend-url/send-emails/", data);
      setStatus(res.data.message || "Emails sent successfully!");
    } catch (error) {
      console.error(error);
      setStatus("Error sending emails.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-center">Bulk Mailer</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            name="email"
            placeholder="Your Email (e.g., you@ganait.com)"
            value={formData.email}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />

          <input
            type="password"
            name="password"
            placeholder="App Password / SMTP Password"
            value={formData.password}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />

          <input
            type="text"
            name="smtpServer"
            placeholder="SMTP Server (e.g., smtp.gmail.com)"
            value={formData.smtpServer}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />

          <input
            type="number"
            name="smtpPort"
            placeholder="SMTP Port (e.g., 587)"
            value={formData.smtpPort}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />

          <input
            type="text"
            name="subject"
            placeholder="Email Subject (can include $name)"
            value={formData.subject}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />

          <textarea
            name="body"
            placeholder="Email body. Use $name to customize."
            value={formData.body}
            onChange={handleChange}
            rows={6}
            required
            className="w-full p-3 border rounded"
          />

          <input
            type="file"
            name="file"
            accept=".csv,.xlsx,.json"
            onChange={handleFileChange}
            required
            className="w-full p-2 border rounded"
          />

          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded w-full"
          >
            Send Bulk Emails
          </button>
        </form>

        {status && (
          <div className="mt-4 text-center text-sm text-gray-700">
            {status}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
