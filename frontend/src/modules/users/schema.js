import { z } from "zod";

export const usersSchema = z.object({
    username: z
        .string()
        .min(3, "Username is too short")
        .max(20, "Username is too long")
        .regex(/^[a-zA-Z0-9._]+$/, "Username is not valid"),

    password: z
        .string()
        .min(8, "Password must be at least 8 characters")
        .max(128, "Password is too long")
        .regex(/[A-Za-z\d@$!%*?&#^]{8,128}$/, "Password is not valid")
        .optional(),

    name: z
        .string()
        .min(3, "Name is too short")
        .max(50, "Name is too long")
        .regex(/^[A-Za-z][A-Za-z0-9 ]{3,49}$/, "Name is not valid"),

    email: z
        .string()
        .regex(/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/, "Email is not valid")
        .optional(),

    phone: z
        .string()
        .length(10, "Phone Number should be 10 digits")
        .regex(/^[6-9]\d{9}$/, "Invalid Number")
        .optional(),

    role: z
        .string()
        .max(10, "Role is too long")
        .regex(/^(admin|manager|staff|guest)$/, "Invalid Roles")
        .optional(),

    image: z
        .string()
        .max(50, "Image filename is too long")
        .regex(/^[A-Za-z0-9_/-]+\.(jpg|jpeg|png)$/, "Invalid Image")
        .optional(),



});