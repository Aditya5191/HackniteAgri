import React, { useState } from "react";

const Chatbot = () => {
  const [messages, setMessages] = useState([]); // State for chat history
  const [input, setInput] = useState(""); // State for user input
  const [loading, setLoading] = useState(false); // Loading state
  const [isExpanded, setIsExpanded] = useState(false); // State for expand/collapse

  // Handle sending a message
  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to chat history
    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      setLoading(true);

      // Send the message to the backend (replace with your API endpoint)
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error("Failed to get a response from the chatbot.");
      }

      const data = await response.json();
      const botMessage = { sender: "bot", text: data.response };

      // Add bot response to chat history
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Sorry, I encountered an error." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.chatContainer}>
      {/* Circular Button (when collapsed) */}
      {!isExpanded && (
        <button onClick={() => setIsExpanded(true)} style={styles.circularButton}>
          <img src="/logo.png" alt="Chatbot Logo" style={styles.logo} />
        </button>
      )}

      {/* Expanded Chatbot */}
      {isExpanded && (
        <div style={styles.expandedChatbot}>
          {/* Chat Window */}
          <div style={styles.chatWindow}>
            {messages.map((msg, index) => (
              <div
                key={index}
                style={
                  msg.sender === "user"
                    ? styles.userMessage
                    : styles.botMessage
                }
              >
                {msg.text}
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div style={styles.inputContainer}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message here..."
              style={styles.input}
            />
            <button
              onClick={sendMessage}
              disabled={loading}
              style={styles.sendButton}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>

          {/* Close Button */}
          <button onClick={() => setIsExpanded(false)} style={styles.closeButton}>
            Close
          </button>
        </div>
      )}
    </div>
  );
};

// Styles
const styles = {
  chatContainer: {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    zIndex: 1000,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  circularButton: {
    width: "60px",
    height: "60px",
    borderRadius: "50%", // Makes the button circular
    backgroundColor: "rgba(255, 255, 255, 0.78)",
    border: "none",
    cursor: "pointer",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    transition: "transform 0.3s ease", // Smooth hover effect
  },
  logo: {
    width: "40px",
    height: "40px",
  },
  expandedChatbot: {
    width: "400px", // Increased width
    height: "500px", // Increased height
    border: "1px solid #ccc",
    borderRadius: "12px",
    padding: "15px",
    backgroundColor: "rgba(0, 0, 0, 0.7)", // Black with transparency
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.2)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  chatWindow: {
    width: "100%",
    height: "400px", // Increased height for chat window
    overflowY: "auto",
    marginBottom: "10px",
    padding: "10px",
    borderRadius: "8px",
    backgroundColor: "rgba(0, 0, 0, 0.17)", // Slightly translucent white background
  },
  userMessage: {
    textAlign: "right", // Align user messages to the right
    backgroundColor: "#007bff", // Blue color for user messages
    color: "#fff",
    padding: "10px 15px",
    borderRadius: "15px",
    margin: "5px 0",
    maxWidth: "80%",
    alignSelf: "flex-end",
  },
  botMessage: {
    textAlign: "left", // Align bot messages to the left
    backgroundColor: "rgba(0, 0, 0, 0.17)", // Light gray color for bot messages
    color: "rgb(255, 255, 255)",
    padding: "10px 15px",
    borderRadius: "15px",
    margin: "5px 0",
    maxWidth: "80%",
    alignSelf: "flex-start",
  },
  inputContainer: {
    display: "flex",
    alignItems: "center",
    width: "100%",
  },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    marginRight: "10px",
    backgroundColor: "#fff", // White background for input box
  },
  sendButton: {
    padding: "10px 15px",
    backgroundColor: "#007bff", // Blue color for send button
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  closeButton: {
    marginTop: "10px",
    padding: "8px 12px",
    backgroundColor: "#dc3545", // Red color for close button
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "14px",
  },
};

export default Chatbot;