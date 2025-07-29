// Configuration
const API_BASE_URL = "http://192.168.0.109:8080"

// DOM Elements
const welcomeSection = document.getElementById("welcome-section")
const interactionContainer = document.getElementById("interaction-container")
const chatHeader = document.getElementById("chat-header")
const chatMessages = document.getElementById("chat-messages")
const storeMap = document.getElementById("store-map")
const chatInputArea = document.getElementById("chat-input-area")
const chatInput = document.getElementById("chat-input")
const sendButton = document.getElementById("send-button")
const statusIndicator = document.getElementById("status-indicator")

// Buttons
const findItemButton = document.getElementById("find-item-button")
const checkPriceButton = document.getElementById("check-price-button")
const viewMapButton = document.getElementById("view-map-button")
const backToChatButton = document.getElementById("back-to-chat")
const backToHomeButton = document.getElementById("back-to-home-button")

// State Management
let isWaitingForResponse = false
let currentView = "welcome" // 'welcome', 'chat', 'map'
const messageHistory = []

// Store Layout Configuration
const aisleLayout = {
  1: "Fresh Produce",
  2: "Fresh Produce",
  3: "Dairy & Refrigerated",
  4: "Frozen Foods",
  5: "Frozen Foods",
  6: "Bakery",
  7: "Bakery & Bread",
  8: "Pantry & Dry Goods",
  9: "Breakfast & Cereal",
  10: "Snacks & Candy",
  11: "Beverages",
  12: "Health & Beauty",
  13: "Household Items",
  14: "Electronics",
  15: "Meat & Seafood",
  16: "Deli",
}

// Enhanced UI State Manager
const UIStateManager = {
  currentState: "welcome",

  setState: (newState) => {
    UIStateManager.currentState = newState
    document.body.setAttribute("data-current-view", newState)
  },

  getState: () => UIStateManager.currentState,
}

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  console.log("🛒 Walmart Co-Pilot Initializing...")

  initializeStoreMap()
  checkBackendStatus()
  setupEventListeners()
  setupEnhancedInteractions()

  // Set up periodic status checks
  setInterval(checkBackendStatus, 30000)

  // Add initial animations
  setTimeout(() => {
    welcomeSection.classList.add("fade-in")
  }, 100)

  console.log("✅ Walmart Co-Pilot Ready!")
})

// Enhanced Event Listeners Setup
function setupEventListeners() {
  // Primary action buttons
  findItemButton.addEventListener("click", () => {
    showChatView()
    chatInput.value = ""
    setTimeout(() => chatInput.focus(), 100)
  })

  checkPriceButton.addEventListener("click", () => {
    showChatView()
    chatInput.value = "How can I check the price of an item?"
    setTimeout(() => sendMessage(), 200)
  })

  // Navigation buttons
  viewMapButton.addEventListener("click", () => {
    showMapView()
  })

  backToChatButton.addEventListener("click", showChatView)
  backToHomeButton.addEventListener("click", showWelcomeView)

  // Chat functionality
  sendButton.addEventListener("click", () => {
    sendMessage()
  })

  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  })

  // Enhanced input interactions
  chatInput.addEventListener("focus", function () {
    this.parentElement.classList.add("focused")
  })

  chatInput.addEventListener("blur", function () {
    this.parentElement.classList.remove("focused")
  })

  // Global click handlers
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("quick-action")) {
      const message = e.target.dataset.message
      chatInput.value = message
      setTimeout(() => sendMessage(), 200)
    } else if (e.target.closest(".quick-map-button")) {
      setTimeout(() => showMapView(), 200)
    }
  })
}

// Enhanced Interactions Setup
function setupEnhancedInteractions() {
  // Enhanced keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (UIStateManager.getState() === "chat" || UIStateManager.getState() === "map") {
        showWelcomeView()
      }
    }
  })
}

// View Management Functions
function showWelcomeView() {
  console.log("📱 Switching to Welcome View")

  interactionContainer.classList.add("hidden")
  interactionContainer.classList.remove("flex")
  welcomeSection.classList.remove("hidden")
  welcomeSection.classList.add("fade-in")

  UIStateManager.setState("welcome")
  currentView = "welcome"
}

function showChatView() {
  console.log("💬 Switching to Chat View")

  welcomeSection.classList.add("hidden")
  interactionContainer.classList.remove("hidden")
  interactionContainer.classList.add("flex", "slide-up")

  storeMap.classList.add("hidden")
  chatHeader.classList.remove("hidden")
  chatMessages.classList.remove("hidden")
  chatInputArea.classList.remove("hidden")

  UIStateManager.setState("chat")
  currentView = "chat"

  setTimeout(() => chatInput.focus(), 300)

  // Initialize chat if empty
  if (chatMessages.children.length === 0) {
    addMessage("Hi! I'm Wallaby, your Walmart shopping assistant. What can I help you find today?", false)
    setTimeout(() => addQuickActions(), 500)
  }
}

function showMapView() {
  console.log("🗺️ Switching to Map View")

  welcomeSection.classList.add("hidden")
  interactionContainer.classList.remove("hidden")
  interactionContainer.classList.add("flex")

  chatHeader.classList.add("hidden")
  chatMessages.classList.add("hidden")
  chatInputArea.classList.add("hidden")
  storeMap.classList.remove("hidden")
  storeMap.classList.add("fade-in")

  UIStateManager.setState("map")
  currentView = "map"
}

// Store Map Initialization
function initializeStoreMap() {
  console.log("🏪 Initializing Store Map...")

  const mapContainer = storeMap.querySelector(".grid")
  mapContainer.innerHTML = ""

  Object.entries(aisleLayout).forEach(([aisleNum, aisleName], index) => {
    const aisleButton = document.createElement("button")
    aisleButton.className = "bg-white hover:bg-gray-50 p-4 rounded-xl text-center border border-gray-200 shadow-sm"
    aisleButton.innerHTML = `
            <div class="font-bold text-lg">${aisleNum}</div>
            <div class="text-xs text-gray-600">${aisleName}</div>
        `
    aisleButton.dataset.aisle = aisleNum
    aisleButton.setAttribute("aria-label", `Aisle ${aisleNum}: ${aisleName}`)

    // Add staggered entrance animation
    aisleButton.style.animationDelay = `${index * 50}ms`
    aisleButton.classList.add("fade-in")

    aisleButton.addEventListener("click", () => {
      showChatView()
      chatInput.value = `What's in aisle ${aisleNum}?`
      setTimeout(() => sendMessage(), 300)
    })

    mapContainer.appendChild(aisleButton)
  })

  console.log("✅ Store Map Initialized")
}

// Aisle Highlighting System
function highlightAisles(aisles) {
  console.log("🎯 Highlighting aisles:", aisles)

  // Clear existing highlights
  document.querySelectorAll("[data-aisle]").forEach((button) => {
    button.classList.remove("aisle-highlight")
  })

  // Apply new highlights with animation
  if (aisles && aisles.length > 0) {
    aisles.forEach((aisleNum, index) => {
      const aisleButton = document.querySelector(`[data-aisle="${aisleNum}"]`)
      if (aisleButton) {
        setTimeout(() => {
          aisleButton.classList.add("aisle-highlight")
          aisleButton.classList.add("bounce")
        }, index * 100)
      }
    })
  }
}

// Backend Status Management
async function checkBackendStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: "GET",
      timeout: 5000,
    })

    if (response.ok) {
      statusIndicator.classList.add("online")
      statusIndicator.title = "Backend Online - Ready to assist!"
      console.log("✅ Backend Status: Online")
    } else {
      throw new Error(`HTTP ${response.status}`)
    }
  } catch (error) {
    statusIndicator.classList.remove("online")
    statusIndicator.title = "Backend Offline - Limited functionality"
    console.warn("⚠️ Backend Status: Offline", error.message)
  }
}

// Enhanced Time Utilities
function getCurrentTime() {
  const now = new Date()
  return now.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  })
}

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return "Good morning"
  if (hour < 17) return "Good afternoon"
  return "Good evening"
}

// Enhanced Message System
function addMessage(content, isUser = false, isTyping = false) {
  console.log(`💬 Adding message: ${isUser ? "User" : "System"}`, { content: content.substring(0, 50) + "..." })

  // Clean up previous quick actions and map containers
  const elementsToRemove = chatMessages.querySelectorAll(".quick-actions-container, .quick-map-container")
  elementsToRemove.forEach((el) => {
    el.style.animation = "fadeOut 0.3s ease-out"
    setTimeout(() => el.remove(), 300)
  })

  if (isTyping) {
    const typingDiv = document.createElement("div")
    typingDiv.className = "typing-container"
    typingDiv.id = "typing-indicator"
    typingDiv.innerHTML = `
            <div class="profile-avatar system-avatar">
                🛒
            </div>
            <div class="typing-bubble">
                <div class="thinking-dots">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>
        `
    chatMessages.appendChild(typingDiv)
    typingDiv.classList.add("slideInUp")
  } else {
    const chatContainer = document.createElement("div")
    chatContainer.className = `chat-container ${isUser ? "user-chat-container" : ""}`

    const timestamp = getCurrentTime()
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    if (isUser) {
      chatContainer.innerHTML = `
                <div class="profile-avatar user-avatar">
                    👤
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-time">${timestamp}</span>
                        <span>You</span>
                    </div>
                    <div class="user-message" id="${messageId}">
                        ${content}
                    </div>
                </div>
            `
    } else {
      chatContainer.innerHTML = `
                <div class="profile-avatar system-avatar">
                    🛒
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span>Wallaby Assistant</span>
                        <span class="message-time">${timestamp}</span>
                    </div>
                    <div class="system-message" id="${messageId}">
                        ${content}
                    </div>
                </div>
            `
    }

    chatMessages.appendChild(chatContainer)
    chatContainer.classList.add("slideInUp")

    // Store message in history
    messageHistory.push({
      id: messageId,
      content: content,
      isUser: isUser,
      timestamp: timestamp,
    })
  }

  // Enhanced scroll to bottom
  setTimeout(() => {
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: "smooth",
    })
  }, 100)
}

function removeTypingIndicator() {
  const typingIndicator = document.getElementById("typing-indicator")
  if (typingIndicator) {
    typingIndicator.style.animation = "fadeOut 0.3s ease-out"
    setTimeout(() => typingIndicator.remove(), 300)
  }
}

// Enhanced Quick Actions
function addQuickActions() {
  const quickActionsDiv = document.createElement("div")
  quickActionsDiv.className = "mb-4 quick-actions-container"
  quickActionsDiv.innerHTML = `
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-4 border border-blue-100">
            <p class="text-sm text-gray-700 mb-3 font-medium flex items-center">
                <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Try asking me:
            </p>
            <div class="grid grid-cols-1 gap-2">
                <button class="quick-action text-blue-700 font-medium w-full flex text-left" 
                        data-message="Where is milk?" 
                        aria-label="Ask where milk is located">
                    <span class="mr-3">🥛</span>
                    <span>Where is milk?</span>
                </button>
                <button class="quick-action text-blue-700 font-medium w-full flex text-left" 
                        data-message="I need bread, eggs, and pasta" 
                        aria-label="Ask for help finding bread, eggs, and pasta">
                    <span class="mr-3">🛒</span>
                    <span>I need bread, eggs, and pasta</span>
                </button>
                <button class="quick-action text-blue-700 font-medium w-full flex text-left" 
                        data-message="Help me find ingredients for spaghetti" 
                        aria-label="Ask for help finding spaghetti ingredients">
                    <span class="mr-3">🍝</span>
                    <span>Help me find ingredients for spaghetti</span>
                </button>
            </div>
        </div>
    `

  chatMessages.appendChild(quickActionsDiv)
  quickActionsDiv.classList.add("slideInUp")
  chatMessages.scrollTo({
    top: chatMessages.scrollHeight,
    behavior: "smooth",
  })
}

function addQuickMapButton(aisles) {
  if (aisles && aisles.length > 0) {
    const mapActionDiv = document.createElement("div")
    mapActionDiv.className = "flex justify-start mt-3 quick-map-container"
    mapActionDiv.innerHTML = `
            <button class="quick-map-button flex items-center" 
                    aria-label="View highlighted aisles on map">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                View on Map
            </button>
        `

    chatMessages.appendChild(mapActionDiv)
    mapActionDiv.classList.add("slideInUp")
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: "smooth",
    })
  }
}

// Enhanced Message Sending
async function sendMessage() {
  const message = chatInput.value.trim()
  if (!message || isWaitingForResponse) {
    console.warn("⚠️ Cannot send message:", { message, isWaitingForResponse })
    return
  }

  console.log("📤 Sending message:", message)

  // Add user message with enhanced animation
  addMessage(message, true)
  chatInput.value = ""

  // Show typing indicator
  addMessage("", false, true)

  // Update UI state
  isWaitingForResponse = true
  sendButton.disabled = true
  chatInput.disabled = true
  sendButton.classList.add("loading")

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ message: message }),
    })

    removeTypingIndicator()

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP ${response.status}: ${errorText}`)
    }

    const data = await response.json()
    console.log("📥 Received response:", data)

    let responseContent = data.message || "I had trouble generating a response."

    // Enhanced cost display
    if (data.individual_item_costs && Object.keys(data.individual_item_costs).length > 0) {
      let costListHtml = `
                <div class="item-list mt-3">
                    <div class="flex items-center mb-2">
                        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                        </svg>
                        <strong class="text-blue-800">Individual Prices:</strong>
                    </div>
                    <div class="space-y-1">
            `

      for (const [item, price] of Object.entries(data.individual_item_costs)) {
        costListHtml += `
                    <div class="flex justify-between items-center py-2 px-3 bg-white rounded-lg border border-blue-100">
                        <span class="text-blue-700 font-medium">${item}</span>
                        <span class="text-blue-800 font-bold">$${price.toFixed(2)}</span>
                    </div>
                `
      }
      costListHtml += "</div></div>"
      responseContent += costListHtml
    }

    // Enhanced total cost display
    if (data.total_cost && data.total_cost > 0) {
      responseContent += `
                <div class="cost-card mt-3">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M16 11V7a4 4 0 00-8 0v4M5 9h14l-1 12H6L5 9z"></path>
                            </svg>
                            <span class="font-semibold">Estimated Total</span>
                        </div>
                        <span class="text-2xl font-bold">$${data.total_cost.toFixed(2)}</span>
                    </div>
                </div>
            `
    }

    addMessage(responseContent, false)

    // Handle aisle highlighting
    if (data.aisles && data.aisles.length > 0) {
      highlightAisles(data.aisles)
      setTimeout(() => addQuickMapButton(data.aisles), 500)
    }
  } catch (error) {
    removeTypingIndicator()
    console.error("❌ Error sending message:", error)

    let errorMessage = "Sorry, I'm having trouble connecting to the server."
    if (error.message.includes("Failed to fetch")) {
      errorMessage += " Please check that the backend server is running."
    }

    addMessage(
      `
            <div class="p-4 rounded-xl bg-red-100 border border-red-200 text-red-800">
                <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    ${errorMessage}
                </div>
            </div>
        `,
      false,
    )
  } finally {
    // Reset UI state
    isWaitingForResponse = false
    sendButton.disabled = false
    chatInput.disabled = false
    sendButton.classList.remove("loading")

    setTimeout(() => chatInput.focus(), 100)
    console.log("✅ Message sending complete")
  }
}

// Enhanced Error Handling
window.addEventListener("error", (e) => {
  console.error("🚨 Global Error:", e.error)
})

window.addEventListener("unhandledrejection", (e) => {
  console.error("🚨 Unhandled Promise Rejection:", e.reason)
})

// Accessibility Enhancements
function announceToScreenReader(message) {
  const announcement = document.createElement("div")
  announcement.setAttribute("aria-live", "polite")
  announcement.setAttribute("aria-atomic", "true")
  announcement.className = "sr-only"
  announcement.textContent = message

  document.body.appendChild(announcement)

  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

// Export for potential future use
window.WalmartCoPilot = {
  UIStateManager,
  messageHistory,
  currentView: () => currentView,
  version: "2.0.0",
}

console.log("🎉 Walmart In-Store Co-Pilot v2.0.0 Fully Loaded!")
