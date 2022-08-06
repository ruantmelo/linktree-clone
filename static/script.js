addSummaryElement = document.querySelector(".add-summary");
summaryInputElement = document.querySelector("#summary-input");
summaryContainerElement = document.querySelector(".summary-container");
summaryEditElement = document.querySelector(".edit-summary");

addSummaryElement.addEventListener("click", function(e) {
    e.preventDefault();

    summaryContainerElement.classList.remove("hidden");
    summaryInputElement.focus();
    summaryInputElement.readOnly = false;
    e.target.classList.add("hidden");
});


summaryInputElement.addEventListener("blur", async function(e) {
    e.preventDefault();
   

    const summary = summaryInputElement.value;

    if(summary.length <= 0){
        summaryContainerElement.classList.add("hidden");
        summaryEditElement.classList.add("hidden");
        addSummaryElement.classList.remove("hidden");
    }else{
        summaryEditElement.classList.remove("hidden");
        summaryInputElement.readOnly = true;
    }

   
    console.log("NEW SUMMARY: ", summaryInputElement.value);


    try{ 
        await fetch("/edit", { headers: {
            "Content-Type": "application/json"
        }, credentials: "include", method: "POST", body: JSON.stringify({summary: summary})})
    }
    catch(e){
        console.log(e);
    }
})


summaryEditElement.addEventListener("click", function(e) {
    e.preventDefault();
    summaryEditElement.classList.add("hidden");
    summaryInputElement.readOnly = false;
    summaryInputElement.focus();
});


summaryInputElement.addEventListener("keydown", function(e) {
    if(e.keyCode === 13){
        e.preventDefault();
        summaryInputElement.blur();
    }
});

summaryInputElement.addEventListener("blur", function(e) {
    e.preventDefault();
    summaryInputElement.readOnly = true;
    summaryEditElement.classList.remove("hidden");
});


// addSummaryElement = document.querySelector(".add-summary");
nameInputElement = document.querySelector("#name-input");
lastNameValue = nameInputElement.value;
// summaryContainerElement = document.querySelector(".summary-container");
nameEditElement = document.querySelector(".edit-name");

nameEditElement.addEventListener("click", function(e) {
    e.preventDefault();
    nameEditElement.classList.add("hidden");
    nameInputElement.readOnly = false;
    nameInputElement.focus();
})

nameInputElement.addEventListener("focus", async function(e) {
    lastNameValue = nameInputElement.value;
})

nameInputElement.addEventListener("blur", async function(e) {
    e.preventDefault();
    const name = nameInputElement.value;

    if(name.length <= 0){
        nameInputElement.value = lastNameValue;
        nameInputElement.readOnly = true;
        nameEditElement.classList.remove("hidden");
    }

    try{ 
        await fetch("/edit", { headers: {
            "Content-Type": "application/json"
        }, credentials: "include", method: "POST", body: JSON.stringify({name: name})})
    }
    catch(e){
        console.log(e);
        nameInputElement.value = lastNameValue;
    }

    nameInputElement.readOnly = true;
    nameEditElement.classList.remove("hidden")

}
)

nameInputElement.addEventListener("keydown", function(e) {
    if(e.keyCode === 13){
        e.preventDefault();
        nameInputElement.blur();
    }
});
