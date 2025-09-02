document.addEventListener("DOMContentLoaded", function () {
    // Apply client-side validation to forms
    const forms = document.querySelectorAll("form");

    Array.from(forms).forEach(form => {
        form.addEventListener("submit", function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                alert("Please fill all required fields correctly.");
            }
            form.classList.add("was-validated");
        }, false);
    });

    // Example: validate CVSS score range (0.0 - 10.0)
    const cvssInput = document.getElementById("vuln_cvss_score");
    if (cvssInput) {
        cvssInput.addEventListener("input", function () {
            const value = parseFloat(cvssInput.value);
            if (isNaN(value) || value < 0 || value > 10) {
                cvssInput.setCustomValidity("CVSS score must be between 0.0 and 10.0");
            } else {
                cvssInput.setCustomValidity("");
            }
        });
    }

    // Example: validate CVSS vector format (basic pattern only)
    const vectorInput = document.getElementById("vuln_cvss_vector");
    if (vectorInput) {
        vectorInput.addEventListener("input", function () {
            const pattern = /^AV:[NALP]\/AC:[LH]\/PR:[NLH]\/UI:[NR]\/S:[UC]\/C:[HLN]\/I:[HLN]\/A:[HLN]/;
            if (!pattern.test(vectorInput.value)) {
                vectorInput.setCustomValidity("Invalid CVSS vector format.");
            } else {
                vectorInput.setCustomValidity("");
            }
        });
    }
});
