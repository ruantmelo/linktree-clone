btnAddLink = document.querySelector("#btn-add-link");
formAddLink = document.querySelector("#form-add-link");
closeAddLink = document.querySelector("#close-add-link");

formAddLink.addEventListener("submit", async function(e) {
    e.preventDefault();
    const labelElement = formAddLink.label;
    const urlElement = formAddLink.url;

    console.log("values ", labelElement.value, urlElement.value);
   
    // console.log("NEW LINK: ", link);
    // formAddLink.querySelector("input").value = "";
    // formAddLink.querySelector("input").focus();
    try{
        await fetch("/edit", { headers: {
            "Content-Type": "application/json"
        }, credentials: "include", method: "POST", body: JSON.stringify({link: { label: labelElement.value, url: urlElement.value}})})

        labelElement.value = "";
        urlElement.value = "";
        closeAddLink.click();
        document.location.href = '/edit'

    }
    catch(e){
        console.log(e);
    }


}
);

btnAddSocialNetwork = document.querySelector("#btn-add-social-network");
formAddSocialNetwork = document.querySelector("#form-add-social-network");
closeAddSocialNetwork = document.querySelector("#close-add-social-network");


formAddSocialNetwork.addEventListener("submit", async function(e) {
    e.preventDefault();
    const idSelectElement = formAddSocialNetwork.idSelect;
    const urlElement = formAddSocialNetwork.url;

    console.log("values ", idSelectElement.value , urlElement.value);

    try{
        const response = await fetch("/edit", { headers: {
            "Content-Type": "application/json"
        }, credentials: "include", method: "POST", body: JSON.stringify({social_network: { id: idSelectElement.value, url: urlElement.value}})})
    
        console.log("response")
        idSelectElement.value = "";
        urlElement.value = "";
        closeAddSocialNetwork.click();
        document.location.href = '/edit'

    }catch(e){
        console.log(e);
    }
});

async function delete_user_social_network(id){
    try{
        await fetch(`/users-social-networks/${id}`, { headers: {
            "Content-Type": "application/json"
        }, credentials: "include", method: "DELETE"})

        document.location.href = '/edit'
    }catch(e){
        console.log(e);
    }
}


async function delete_user_link(id){
    try{
        await fetch(`/links/${id}`, { headers: {
            "Content-Type": "application/json"
        }, credentials: "include", method: "DELETE"})

        document.location.href = '/edit'
    }catch(e){
        console.log(e);
    }
}




// btnAddLink.addEventListener("click", function(e) {
//     e.preventDefault();
//     linkContainerElement.classList.remove("hidden");
//     linkInputElement.focus();
//     linkInputElement.readOnly = false;
//     e.target.classList.add("hidden");
// }

