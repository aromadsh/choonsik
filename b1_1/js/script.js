/* Declaration */

const hamburgerButton = document.querySelector(".hamburger-button");
const navMenu = document.querySelector(".nav-menu");
const pageLinks = document.querySelectorAll('a[href^="#"]');
const scrollTopButton = document.querySelector("#scroll-top-button");
const themeButton = document.querySelector(".theme-button");
const header = document.querySelector(".header");
const revealElements = document.querySelectorAll(".reveal");
const contactForm = document.querySelector("#contact-form");
const nameInput = document.querySelector("#name");
const emailInput = document.querySelector("#email");
const messageInput = document.querySelector("#message");
const nameError = document.querySelector("#name-error");
const emailError = document.querySelector("#email-error");
const messageError = document.querySelector("#message-error");
const formSuccess = document.querySelector("#form-success");


/* Theme */

const applyTheme = (theme) => {

  document.documentElement.setAttribute(
    "data-theme",
    theme
  );

  themeButton.textContent =
    theme === "dark" ? "Light" : "Dark";
};


const savedTheme =
  localStorage.getItem("theme");


let currentTheme =
  savedTheme === "dark" ? "dark" : "light";


applyTheme(currentTheme);


themeButton.addEventListener("click", () => {

  currentTheme =
    currentTheme === "light" ? "dark" : "light";

  applyTheme(currentTheme);

  localStorage.setItem(
    "theme",
    currentTheme
  );

});


/* Hamburger Menu */

hamburgerButton.addEventListener("click", () => {

  navMenu.classList.toggle("active");

  const isOpen = navMenu.classList.contains("active");

  hamburgerButton.setAttribute(
    "aria-expanded",
    isOpen
  );

});


/* Smooth Scroll */

pageLinks.forEach((link) => {

  link.addEventListener("click", (event) => {

    const targetId =
      link.getAttribute("href");

    if (targetId === "#") {
      event.preventDefault();
      return;
    }

    const targetSection = document.querySelector(targetId);

    if (!targetSection) {
      return;
    }

    event.preventDefault();

    targetSection.scrollIntoView({
      behavior: "smooth"
    });

    navMenu.classList.remove("active");

    hamburgerButton.setAttribute(
      "aria-expanded",
      "false"
    );

  });

});


/* Scroll Event */

window.addEventListener("scroll", () => {

  if (window.scrollY >= 300) {
    scrollTopButton.classList.add("show");
  } else {
    scrollTopButton.classList.remove("show");
  }


  if (window.scrollY >= 60) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }

});


/* Scroll Top */

scrollTopButton.addEventListener("click", () => {

  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });

});


/* Intersection Observer */

const observer =
  new IntersectionObserver(
    (entries) => {

      entries.forEach((entry) => {

        if (entry.isIntersecting) {

          entry.target.classList.add(
            "visible"
          );

          observer.unobserve(
            entry.target
          );

        }

      });

    },
    {
      threshold: 0.2
    }
  );


revealElements.forEach((element) => {
  observer.observe(element);
});


/* Contact Form */

const formState = {
    name: "",
    email: "",
    message: "",

    errors: {
        name: "",
        email: "",
        message: ""
    }
};

const validateName = (value) => {
    if (value.trim() === "") {
        return "이름을 입력해주세요.";
    }
    return "";
};

const validateEmail = (value) => {
    const trimmedValue = value.trim();

    if (trimmedValue === "") {
        return "이메일을 입력해주세요.";
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(trimmedValue)) {
        return "올바른 이메일 형식을 입력해주세요."
    }
    return "";
}

const validateMessage = (value) => {
    if (value.trim() === "") {
        return "메시지를 입력해주세요.";
    }
    return "";
};