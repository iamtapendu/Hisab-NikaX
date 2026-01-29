import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from "../src/app/providers/AuthProvider";
import { router } from "./app/router"
import './global.css'


const root = document.getElementById("root");

// Remove boot loader once React starts
const bootLoader = document.getElementById("boot-loader");
if (bootLoader) bootLoader.remove();

createRoot(root).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router}></RouterProvider>
    </AuthProvider>
  </StrictMode>,
)
