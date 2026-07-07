// =============================================================================
# Credit Repair CRM & Dispute Generator — Core Frontend Engine
# Rick Jefferson | RJ Business Solutions
# 📍 1342 NM 333, Tijeras, New Mexico 87059
# 🌐 https://rickjeffersonsolutions.com
# =============================================================================

document.addEventListener("DOMContentLoaded", () => {
    // Portals & Tabs
    const tabCrmBtn = document.getElementById("tab-crm-btn");
    const tabDisputeBtn = document.getElementById("tab-dispute-btn");
    const viewCrm = document.getElementById("view-crm");
    const viewDispute = document.getElementById("view-dispute");

    // Intake Form & CRM Directory
    const intakeForm = document.getElementById("intake-form");
    const clientNameInput = document.getElementById("client-name");
    const clientEmailInput = document.getElementById("client-email");
    const clientPhoneInput = document.getElementById("client-phone");
    const crmDirectoryList = document.getElementById("crm-directory-list");
    const totalClientsCount = document.getElementById("total-clients-count");

    // Dispute Generator
    const disputeClientSelect = document.getElementById("dispute-client-select");
    const disputeBureauSelect = document.getElementById("dispute-bureau-select");
    const disputeReportItems = document.getElementById("dispute-report-items");
    const disputeItemNameInput = document.getElementById("dispute-item-name");
    const disputeAccountNumberInput = document.getElementById("dispute-account-number");
    const disputeTypeSelect = document.getElementById("dispute-type-select");
    const disputeReasonTextInput = document.getElementById("dispute-reason-text");
    const generateLetterBtn = document.getElementById("generate-letter-btn");

    // Previews & Transmit
    const disputePreviewSection = document.getElementById("dispute-preview-section");
    const letterPreviewContent = document.getElementById("letter-preview-content");
    const printLetterBtn = document.getElementById("print-letter-btn");
    const emailLetterBtn = document.getElementById("email-letter-btn");
    const printSheet = document.getElementById("print-sheet");

    // Global memory cache
    let cachedClients = [];
    let activeClientDetails = null;
    let activeGeneratedLetter = null;

    // --- Tab Controllers ---
    tabCrmBtn.addEventListener("click", () => switchTab("crm"));
    tabDisputeBtn.addEventListener("click", () => switchTab("dispute"));

    function switchTab(target) {
        if (target === "crm") {
            tabCrmBtn.className = "w-full text-left py-3 px-4 rounded-xl text-slate-100 bg-slate-800 hover:bg-slate-800 font-medium transition flex items-center gap-3";
            tabDisputeBtn.className = "w-full text-left py-3 px-4 rounded-xl text-slate-400 hover:bg-slate-800/50 hover:text-slate-100 font-medium transition flex items-center gap-3";
            viewCrm.classList.remove("hidden");
            viewCrm.classList.add("flex");
            viewDispute.classList.add("hidden");
            viewDispute.classList.remove("flex");
        } else {
            tabDisputeBtn.className = "w-full text-left py-3 px-4 rounded-xl text-slate-100 bg-slate-800 hover:bg-slate-800 font-medium transition flex items-center gap-3";
            tabCrmBtn.className = "w-full text-left py-3 px-4 rounded-xl text-slate-400 hover:bg-slate-800/50 hover:text-slate-100 font-medium transition flex items-center gap-3";
            viewDispute.classList.remove("hidden");
            viewDispute.classList.add("flex");
            viewCrm.classList.add("hidden");
            viewCrm.classList.remove("flex");
        }
    }

    // --- Load Clients ---
    async function loadClients() {
        try {
            const res = await fetch("/api/clients");
            const data = await res.json();
            cachedClients = data;
            
            // Render CRM Directory
            renderCrmDirectory(data);
            totalClientsCount.textContent = `${data.length} Active Clients`;

            // Populate Dispute Selector
            disputeClientSelect.innerHTML = `<option value="">Choose a client...</option>` + 
                data.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
        } catch (err) {
            console.error("Error loading clients:", err);
        }
    }

    // --- Client Intake Form Submit ---
    intakeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const payload = {
            name: clientNameInput.value.trim(),
            email: clientEmailInput.value.trim(),
            phone: clientPhoneInput.value.trim()
        };

        try {
            const res = await fetch("/api/clients", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.success) {
                // Clear inputs
                clientNameInput.value = "";
                clientEmailInput.value = "";
                clientPhoneInput.value = "";
                
                // Refresh client directory
                await loadClients();
                
                // Show MyFreeScoreNow Signup overlay alert
                alert(
                    `Success: Client Added!\n\n` + 
                    `Mandatory Step: Redirecting to complete the MyFreeScoreNow credit report monitoring checks:\n` +
                    `${data.enrollment_url}\n\n` + 
                    `Click OK to open the affiliate tracking checkout portal.`
                );
                window.open(data.enrollment_url, "_blank");
            } else {
                alert(`Error: ${data.error || "Failed to add client."}`);
            }
        } catch (err) {
            alert(`Network Error: ${err.message}`);
        }
    });

    // --- Render CRM Client Cards ---
    function renderCrmDirectory(clients) {
        if (clients.length === 0) {
            crmDirectoryList.innerHTML = `
                <div class="text-center py-12 text-slate-500">
                    <i class="fa-solid fa-users text-4xl mb-3 block text-slate-700"></i>
                    No clients registered yet. Please run an intake.
                </div>
            `;
            return;
        }

        crmDirectoryList.innerHTML = clients.map(client => `
            <div class="p-5 bg-slate-900/40 border border-slate-800/80 rounded-xl hover:border-brand-gold/30 transition flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div class="flex flex-col gap-1.5">
                    <h3 class="text-base font-bold text-slate-100 heading-font">${client.name}</h3>
                    <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
                        <span><i class="fa-solid fa-envelope text-brand-gold mr-1"></i> ${client.email}</span>
                        <span><i class="fa-solid fa-phone text-brand-gold mr-1"></i> ${client.phone}</span>
                        <span><i class="fa-solid fa-hashtag text-brand-gold mr-1"></i> ID: ${client.myfreescorenow_id || "Unregistered"}</span>
                    </div>
                </div>
                <div class="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t border-slate-800/50 md:border-none pt-3 md:pt-0">
                    <!-- Bureau scores badges -->
                    <div class="flex gap-2">
                        <div class="text-center">
                            <span class="block text-[10px] text-slate-500 font-semibold uppercase">EXP</span>
                            <span class="px-2 py-0.5 bg-slate-800 text-slate-300 font-bold rounded text-xs">${client.scores.experian || "N/A"}</span>
                        </div>
                        <div class="text-center">
                            <span class="block text-[10px] text-slate-500 font-semibold uppercase">TU</span>
                            <span class="px-2 py-0.5 bg-slate-800 text-slate-300 font-bold rounded text-xs">${client.scores.transunion || "N/A"}</span>
                        </div>
                        <div class="text-center">
                            <span class="block text-[10px] text-slate-500 font-semibold uppercase">EQ</span>
                            <span class="px-2 py-0.5 bg-slate-800 text-slate-300 font-bold rounded text-xs">${client.scores.equifax || "N/A"}</span>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="selectDisputeClient(${client.id})" class="py-2 px-3 bg-brand-gold hover:bg-yellow-500 text-slate-950 font-bold rounded-lg text-xs transition">
                            Dispute
                        </button>
                        <button onclick="deleteClient(${client.id})" class="p-2 bg-slate-800/80 hover:bg-red-950/60 hover:text-red-400 hover:border-red-900 border border-transparent text-slate-400 rounded-lg transition">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join("");
    }

    // --- Global Click Router for card selects ---
    window.selectDisputeClient = (clientId) => {
        disputeClientSelect.value = clientId;
        triggerClientSelection(clientId);
        switchTab("dispute");
    };

    window.deleteClient = async (clientId) => {
        if (!confirm("Are you sure you want to delete this client?")) return;
        try {
            const res = await fetch(`/api/clients/${clientId}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                loadClients();
            }
        } catch (err) {
            console.error("Error deleting client:", err);
        }
    };

    // --- Dispute Client Selected Trigger ---
    disputeClientSelect.addEventListener("change", (e) => {
        const val = e.target.value;
        if (val) triggerClientSelection(val);
    });

    async function triggerClientSelection(clientId) {
        try {
            disputeReportItems.innerHTML = `
                <tr>
                    <td colspan="5" class="p-6 text-center">
                        <i class="fa-solid fa-circle-notch animate-spin text-xl text-brand-gold mr-2"></i>
                        Pulsing report check with MyFreeScoreNow API...
                    </td>
                </tr>
            `;

            const res = await fetch(`/api/clients/${clientId}`);
            const data = await res.json();
            activeClientDetails = data;
            
            // Render Report Table Items
            renderNegativeItemsTable(data.negative_items);
        } catch (err) {
            disputeReportItems.innerHTML = `
                <tr><td colspan="5" class="p-6 text-center text-red-400">Failed to query API: ${err.message}</td></tr>
            `;
        }
    }

    function renderNegativeItemsTable(items) {
        if (!items || items.length === 0) {
            disputeReportItems.innerHTML = `
                <tr><td colspan="5" class="p-6 text-center text-slate-500">No negative items found on active credit file.</td></tr>
            `;
            return;
        }

        disputeReportItems.innerHTML = items.map((item, idx) => `
            <tr class="border-b border-slate-800/80 hover:bg-slate-900/30 transition text-slate-300">
                <td class="p-3 font-semibold text-brand-gold">${item.bureau}</td>
                <td class="p-3 font-medium text-slate-200">${item.item_name}</td>
                <td class="p-3 font-mono">${item.account_number}</td>
                <td class="p-3"><span class="px-2 py-0.5 bg-slate-800 border border-slate-700 text-slate-300 rounded text-xs">${item.type}</span></td>
                <td class="p-3 text-right">
                    <button onclick="autofillDisputeFields(${idx})" class="py-1 px-2.5 bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold rounded text-xs transition">
                        Select
                    </button>
                </td>
            </tr>
        `).join("");
    }

    window.autofillDisputeFields = (idx) => {
        if (!activeClientDetails || !activeClientDetails.negative_items[idx]) return;
        const item = activeClientDetails.negative_items[idx];
        
        disputeBureauSelect.value = item.bureau;
        disputeItemNameInput.value = item.item_name;
        disputeAccountNumberInput.value = item.account_number;
        disputeReasonTextInput.value = item.reason;
        
        // Match selection to select type dropdown
        if (item.type.toLowerCase().includes("collection")) {
            disputeTypeSelect.value = "Collection";
        } else if (item.type.toLowerCase().includes("late")) {
            disputeTypeSelect.value = "Late Payment";
        } else if (item.type.toLowerCase().includes("charge")) {
            disputeTypeSelect.value = "Charge Off";
        } else {
            disputeTypeSelect.value = "Inquiry";
        }
    };

    // --- Generate Bureau Dispute Letter ---
    generateLetterBtn.addEventListener("click", async () => {
        const clientId = disputeClientSelect.value;
        if (!clientId) {
            alert("Please select a client first.");
            return;
        }
        
        const payload = {
            client_id: parseInt(clientId),
            bureau: disputeBureauSelect.value,
            item_name: disputeItemNameInput.value.trim(),
            account_number: disputeAccountNumberInput.value.trim(),
            dispute_reason: disputeReasonTextInput.value.trim(),
            dispute_type: disputeTypeSelect.value
        };

        if (!payload.item_name || !payload.account_number || !payload.dispute_reason) {
            alert("Please fill in item name, account number, and dispute reason details.");
            return;
        }

        try {
            generateLetterBtn.disabled = true;
            generateLetterBtn.textContent = "Compiling Letter Template...";

            const res = await fetch("/api/disputes/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.success) {
                activeGeneratedLetter = data;
                
                // Inject today's date formatted
                const dateOptions = { year: 'numeric', month: 'long', day: 'numeric' };
                const todayStr = new Date().toLocaleDateString("en-US", dateOptions);
                const completeContent = data.letter_content.replace("[Current Date]", todayStr);
                
                activeGeneratedLetter.content = completeContent;
                
                letterPreviewContent.textContent = completeContent;
                disputePreviewSection.classList.remove("hidden");
                disputePreviewSection.scrollIntoView({ behavior: "smooth" });
            } else {
                alert("Failed to generate dispute letter.");
            }
        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            generateLetterBtn.disabled = false;
            generateLetterBtn.textContent = "Generate Bureau Dispute Letter";
        }
    });

    // --- Print Dispute Letter (Hides UI and formats for paper) ---
    printLetterBtn.addEventListener("click", () => {
        if (!activeGeneratedLetter) return;
        
        // Populate and trigger print session
        printSheet.textContent = activeGeneratedLetter.content;
        printSheet.classList.remove("hidden");
        
        window.print();
        
        // Hide again post print
        printSheet.classList.add("hidden");
        printSheet.textContent = "";
    });

    // --- Email Dispute Letter ---
    emailLetterBtn.addEventListener("click", async () => {
        if (!activeGeneratedLetter || !activeClientDetails) return;
        
        const payload = {
            client_id: activeClientDetails.client.id,
            to_email: activeClientDetails.client.email,
            bureau: activeGeneratedLetter.bureau,
            subject: `Ready Credit Dispute Letter - ${activeGeneratedLetter.bureau}`,
            body: activeGeneratedLetter.content
        };

        try {
            emailLetterBtn.disabled = true;
            emailLetterBtn.textContent = "Sending Email...";

            const res = await fetch("/api/disputes/email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.success) {
                alert(`Success: Dispute letter emailed to client at ${payload.to_email}`);
            } else {
                alert(`Error: ${data.error || "Failed to send email."}`);
            }
        } catch (err) {
            alert(`Error transmitting email: ${err.message}`);
        } finally {
            emailLetterBtn.disabled = false;
            emailLetterBtn.textContent = "Email to Client";
        }
    });

    // Initial Loading trigger
    loadClients();
});
