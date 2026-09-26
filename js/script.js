/* Declaration */

const hamburgerButton =
  document.querySelector(".hamburger-button");

const navMenu =
  document.querySelector(".nav-menu");

const pageLinks =
  document.querySelectorAll('a[href^="#"]');

const scrollTopButton =
  document.querySelector("#scroll-top-button");

const themeButton =
  document.querySelector(".theme-button");

const header =
  document.querySelector(".header");

const revealElements =
  document.querySelectorAll(".reveal");

const contactForm =
  document.querySelector("#contact-form");

const nameInput =
  document.querySelector("#name");

const emailInput =
  document.querySelector("#email");

const messageInput =
  document.querySelector("#message");

const nameError =
  document.querySelector("#name-error");

const emailError =
  document.querySelector("#email-error");

const messageError =
  document.querySelector("#message-error");

const formSuccess =
  document.querySelector("#form-success");

const projectsGrid =
  document.querySelector("#projects-grid");

const projectsStatus =
  document.querySelector("#projects-status");

const retryButton =
  document.querySelector("#retry-button");

const projectFilters =
  document.querySelector("#project-filters");

const typingText =
  document.querySelector("#typing-text");


/* Typing Effect */

const typingMessage =
  "데이터를 분석하고\n서비스로 구현합니다.";

let typingIndex = 0;

const typingSpeed = 80;


const typeText = () => {

  if (typingIndex < typingMessage.length) {

    typingText.textContent +=
      typingMessage[typingIndex];

    typingIndex += 1;


    setTimeout(
      typeText,
      typingSpeed
    );

  }

};


typeText();


/* Theme */

const applyTheme = (theme) => {

  document.documentElement.setAttribute(
    "data-theme",
    theme
  );

  themeButton.textContent =
    theme === "dark"
      ? "Light"
      : "Dark";
};


const savedTheme =
  localStorage.getItem("theme");


let currentTheme =
  savedTheme === "dark"
    ? "dark"
    : "light";


applyTheme(currentTheme);


themeButton.addEventListener("click", () => {

  currentTheme =
    currentTheme === "light"
      ? "dark"
      : "light";

  applyTheme(currentTheme);

  localStorage.setItem(
    "theme",
    currentTheme
  );

});


/* Hamburger Menu */

hamburgerButton.addEventListener("click", () => {

  navMenu.classList.toggle("active");

  const isOpen =
    navMenu.classList.contains("active");

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

    const targetSection =
      document.querySelector(targetId);

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

  const trimmedValue =
    value.trim();


  if (trimmedValue === "") {
    return "이메일을 입력해주세요.";
  }


  const emailPattern =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


  if (!emailPattern.test(trimmedValue)) {
    return "올바른 이메일 형식을 입력해주세요.";
  }


  return "";

};


const validateMessage = (value) => {

  if (value.trim() === "") {
    return "메시지를 입력해주세요.";
  }

  return "";

};


const renderFieldError = (
  input,
  errorElement,
  message
) => {

  errorElement.textContent =
    message;

  input.classList.toggle(
    "input-error",
    message !== ""
  );

};


nameInput.addEventListener(
  "input",
  (event) => {

    formState.name =
      event.target.value;

    formState.errors.name =
      validateName(
        formState.name
      );

    renderFieldError(
      nameInput,
      nameError,
      formState.errors.name
    );

    formSuccess.textContent = "";

  }
);


emailInput.addEventListener(
  "input",
  (event) => {

    formState.email =
      event.target.value;

    formState.errors.email =
      validateEmail(
        formState.email
      );

    renderFieldError(
      emailInput,
      emailError,
      formState.errors.email
    );

    formSuccess.textContent = "";

  }
);


messageInput.addEventListener(
  "input",
  (event) => {

    formState.message =
      event.target.value;

    formState.errors.message =
      validateMessage(
        formState.message
      );

    renderFieldError(
      messageInput,
      messageError,
      formState.errors.message
    );

    formSuccess.textContent = "";

  }
);


contactForm.addEventListener(
  "submit",
  (event) => {

    event.preventDefault();


    formState.name =
      nameInput.value;

    formState.email =
      emailInput.value;

    formState.message =
      messageInput.value;


    formState.errors.name =
      validateName(
        formState.name
      );

    formState.errors.email =
      validateEmail(
        formState.email
      );

    formState.errors.message =
      validateMessage(
        formState.message
      );


    renderFieldError(
      nameInput,
      nameError,
      formState.errors.name
    );

    renderFieldError(
      emailInput,
      emailError,
      formState.errors.email
    );

    renderFieldError(
      messageInput,
      messageError,
      formState.errors.message
    );


    const hasError =
      Object.values(
        formState.errors
      ).some((error) => {
        return error !== "";
      });


    if (hasError) {

      formSuccess.textContent = "";

      return;

    }


    formSuccess.textContent =
      "메시지가 정상적으로 확인되었습니다.";


    contactForm.reset();


    formState.name = "";
    formState.email = "";
    formState.message = "";

  }
);


/* GitHub API */

const githubUsername =
  "aromadsh";


const githubApiUrl =
  `https://api.github.com/users/${githubUsername}/repos?sort=updated&per_page=6&type=owner`;


const projectState = {
  status: "loading",
  repos: [],
  error: "",
  filter: "all"
};


const renderFilterButtons = () => {

  const languages = [
    ...new Set(
      projectState.repos
        .map((repo) => {
          return repo.language;
        })
        .filter((language) => {
          return language !== null;
        })
    )
  ];


  const filters = [
    "all",
    ...languages
  ];


  const filterButtons =
    filters.map((language) => {

      const buttonText =
        language === "all"
          ? "All"
          : language;


      const activeClass =
        projectState.filter === language
          ? " active"
          : "";


      return `
        <button
          type="button"
          class="filter-button${activeClass}"
          data-language="${language}"
        >
          ${buttonText}
        </button>
      `;

    });


  projectFilters.innerHTML =
    filterButtons.join("");

};


const renderProjects = () => {

  projectsGrid.innerHTML = "";

  projectFilters.innerHTML = "";

  retryButton.hidden = true;


  if (projectState.status === "loading") {

    projectsStatus.textContent =
      "GitHub 저장소를 불러오는 중입니다.";

    return;

  }


  if (projectState.status === "error") {

    projectsStatus.textContent =
      projectState.error;

    retryButton.hidden = false;

    return;

  }


  if (projectState.status === "empty") {

    projectsStatus.textContent =
      "표시할 공개 저장소가 없습니다.";

    return;

  }


  if (projectState.status === "success") {

    renderFilterButtons();


    const visibleRepos =
      projectState.filter === "all"
        ? projectState.repos
        : projectState.repos.filter((repo) => {
            return repo.language ===
              projectState.filter;
          });


    if (projectState.filter === "all") {

      projectsStatus.textContent =
        `${projectState.repos.length}개의 저장소를 불러왔습니다.`;

    } else {

      projectsStatus.textContent =
        `${projectState.filter} 프로젝트 ${visibleRepos.length}개를 표시합니다.`;

    }


    const projectCards =
      visibleRepos.map((repo) => {

        const {
          name,
          description,
          language,
          stargazers_count,
          html_url
        } = repo;


        return `
          <article class="project-card">

            <h3>${name}</h3>

            <p class="project-description">
              ${description ?? "프로젝트 설명이 없습니다."}
            </p>

            <div class="project-meta">

              <span>
                ${language ?? "언어 정보 없음"}
              </span>

              <span>
                Star ${stargazers_count}
              </span>

            </div>

            <a
              href="${html_url}"
              class="project-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub 보기
            </a>

          </article>
        `;

      });


    projectsGrid.innerHTML =
      projectCards.join("");

  }

};


projectFilters.addEventListener(
  "click",
  (event) => {

    const clickedButton =
      event.target.closest(
        ".filter-button"
      );


    if (!clickedButton) {
      return;
    }


    projectState.filter =
      clickedButton.dataset.language;


    renderProjects();

  }
);


const fetchRepositories = async () => {

  projectState.status =
    "loading";

  projectState.repos =
    [];

  projectState.error =
    "";

  projectState.filter =
    "all";


  renderProjects();


  try {

    const response =
      await fetch(
        githubApiUrl,
        {
          headers: {
            Accept:
              "application/vnd.github+json"
          }
        }
      );


    if (!response.ok) {

      if (response.status === 403) {

        throw new Error(
          "GitHub API 요청 한도를 초과했거나 접근이 제한되었습니다."
        );

      }


      if (response.status === 404) {

        throw new Error(
          "GitHub 사용자를 찾을 수 없습니다."
        );

      }


      throw new Error(
        `GitHub API 요청에 실패했습니다. 상태 코드: ${response.status}`
      );

    }


    const repos =
      await response.json();


    const filteredRepos =
      repos.filter((repo) => {
        return !repo.fork;
      });


    projectState.repos =
      filteredRepos;


    projectState.status =
      filteredRepos.length === 0
        ? "empty"
        : "success";

  } catch (error) {

    projectState.status =
      "error";

    projectState.error =
      error.message;

  }


  renderProjects();

};


retryButton.addEventListener(
  "click",
  () => {

    fetchRepositories();

  }
);


fetchRepositories();