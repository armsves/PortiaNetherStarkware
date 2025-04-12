// Remove Node.js-specific modules (fs and path)

// Function to check if the file exists on the server
async function checkFileExists(id) {
    try {
        const response = await fetch(`/balances/${id}.json`);
        if (response.ok) {
            console.log(`File ${id}.json exists on the server.`);
            const fileContent = await response.json();
            return fileContent; // Return the parsed JSON content
        } else {
            console.log(`File ${id}.json does not exist on the server.`);
            return null;
        }
    } catch (error) {
        console.error("Error checking file existence on the server:", error);
        return null;
    }
}

// Function to save balance to the server
async function saveBalanceToServer(id, balance) {
    try {
        const response = await fetch(`/save-balance`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ id, balance }),
        });

        if (response.ok) {
            console.log(`Balance for ID ${id} saved to the server.`);
        } else {
            console.error("Error saving balance to the server:", await response.text());
        }
    } catch (error) {
        console.error("Error saving balance to the server:", error);
    }
}

// Automatically connect wallet and fetch balance on page load
window.onload = async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get("id");

    console.log(`Page loaded with ID: ${id}`);

    if (!id) {
        console.error("No ID provided in the URL.");
        return;
    }

    // Check if the file exists on the server
    const fileContent = await checkFileExists(id);
    if (fileContent) {
        console.log(`Balance for ID ${id} loaded from server:`, fileContent);
        return; // Exit early since the file exists
    }

    // If the file does not exist, prompt wallet connection
    const isConnected = await connectWallet();
    if (isConnected) {
        const balanceJson = await getBalance();
        console.log(`Balance for ID ${id}:`, balanceJson);
        if (balanceJson) {
            // Save the balance to the server
            await saveBalanceToServer(id, balanceJson);
        }
    }
};