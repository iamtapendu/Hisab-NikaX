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
        .regex(/[A-Za-z\d@$!%*?&#^]{8,128}$/, "Password is not valid"),

    name: z
        .string(),

    email: z
        .string(),

    phone: z
        .string(),

    role:
        z.string(),

    image:
        z.string(),


});