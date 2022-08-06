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
