import React, { useState } from "react";
import axios from "axios";

function App() {
  const [weatherData, setWeatherData] = useState(null);
  const [city, setCity] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [steps, setSteps] = useState([]);

  const fetchWeather = async () => {
    if (!city.trim()) return;

    setLoading(true);
    setError(null);
    setWeatherData(null);
    setSteps([]);

    try {
      const response = await axios.post("http://localhost:8000/api/weather", {
        query: city,
      });

      const data = response.data;

      // Server should return something like:
      // { result: "12 Degree Cel", steps: [{ step: "plan", content: "..." }, ...] }

      setWeatherData(data.result);
      setSteps(data.steps || []);
    } catch (err) {
      setError("Failed to fetch weather.");
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (desc) => {
    const lower = desc.toLowerCase();

    // Checking for specific weather conditions
    if (lower.includes("rain")) return "🌧️"; // Rain
    if (lower.includes("cloud")) return "☁️"; // Cloudy
    if (lower.includes("clear")) return "☀️"; // Clear
    if (lower.includes("snow")) return "❄️"; // Snow
    if (lower.includes("thunderstorm") || lower.includes("storm")) return "🌩️"; // Thunderstorm
    if (lower.includes("fog")) return "🌫️"; // Fog
    if (lower.includes("wind")) return "💨"; // Windy

    // Default to sun icon for unclear weather
    return "🌤️"; // Partly cloudy
  };

  return (
    <div className="min-h-screen bg-zinc-300 text-white flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-xl bg-zinc-700 p-6 rounded-2xl shadow-2xl">
        <h1 className="text-4xl font-bold text-center mb-6 text-blue-400 ">
          🌐 Weather AI
        </h1>

        {/* Input Field */}
        <div className="flex gap-2">
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Enter city"
            className="flex-1 p-3 rounded-lg text-black border-2 border-black focus:outline-none text-white"
          />
          <button
            onClick={fetchWeather}
            className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-md font-semibold"
          >
            Ask
          </button>
        </div>

        {/* Loading / Error */}
        {loading && (
          <p className="mt-4 text-center text-gray-300">⏳ Thinking...</p>
        )}
        {error && <p className="mt-4 text-center text-red-400">{error}</p>}

        {/* Weather Result */}
        {weatherData && !loading && (
          <div className="mt-6 text-center">
            <div className="text-6xl mb-2">{getWeatherIcon(weatherData)}</div>
            <p className="text-xl font-semibold">{weatherData}</p>
          </div>
        )}

        {/* Server Steps */}
        {steps.length > 0 && (
          <div className="mt-8 bg-[#334155] rounded-lg p-4">
            <h2 className="text-lg font-bold mb-3 text-blue-300">
              🤖 AI Thinking:
            </h2>
            <ul className="space-y-2 text-sm text-gray-200">
              {steps.map((step, index) => (
                <li key={index} className="bg-[#475569] px-3 py-2 rounded-md">
                  {step.content || step.output || step.input}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
