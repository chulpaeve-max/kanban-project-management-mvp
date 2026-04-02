import { expect, test } from "@playwright/test";

// Helper to login before each test
test.beforeEach(async ({ page }) => {
  await page.goto("/");
  
  // Check if login form is present
  const loginForm = page.locator('form').filter({ hasText: /sign in/i });
  if (await loginForm.isVisible()) {
    await page.getByPlaceholder(/username/i).fill("user");
    await page.getByPlaceholder(/password/i).fill("password");
    await page.getByRole("button", { name: /sign in/i }).click();
    
    // Wait for board to load
    await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  }
});

test("loads the kanban board from API", async ({ page }) => {
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card and persists after refresh", async ({ page }) => {
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persistent card");
  await firstColumn.getByPlaceholder("Details").fill("Should persist after refresh");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persistent card")).toBeVisible();
  
  // Refresh page
  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  
  // Card should still be there
  await expect(firstColumn.getByText("Persistent card")).toBeVisible();
});

test("renames a column and persists after refresh", async ({ page }) => {
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  const input = firstColumn.getByRole("textbox", { name: /column title/i });
  
  await input.clear();
  await input.fill("Renamed Column");
  await input.blur(); // Trigger the rename
  
  // Wait a bit for API call
  await page.waitForTimeout(500);
  
  // Refresh page
  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  
  // Column name should persist
  await expect(firstColumn.getByRole("textbox", { name: /column title/i })).toHaveValue("Renamed Column");
});

test("deletes a card and persists after refresh", async ({ page }) => {
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  
  // Add a card first
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Card to delete");
  await firstColumn.getByPlaceholder("Details").fill("Will be deleted");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Card to delete")).toBeVisible();
  
  // Delete the card
  const deleteButton = firstColumn.getByRole("button", { name: /delete card to delete/i });
  await deleteButton.click();
  await expect(firstColumn.getByText("Card to delete")).not.toBeVisible();
  
  // Refresh page
  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  
  // Card should still be gone
  await expect(firstColumn.getByText("Card to delete")).not.toBeVisible();
});

test("moves a card between columns and persists", async ({ page }) => {
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  
  // Add a card to move
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Card to move");
  await firstColumn.getByPlaceholder("Details").fill("Will be moved");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Card to move")).toBeVisible();
  
  // Find the card and target column
  const card = page.getByText("Card to move").locator('..');
  const targetColumn = page.locator('[data-testid^="column-"]').nth(2); // Third column
  
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  // Drag and drop
  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  
  // Verify card moved
  await expect(targetColumn.getByText("Card to move")).toBeVisible();
  await expect(firstColumn.getByText("Card to move")).not.toBeVisible();
  
  // Wait for API call
  await page.waitForTimeout(500);
  
  // Refresh page
  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  
  // Card should still be in target column
  await expect(targetColumn.getByText("Card to move")).toBeVisible();
  await expect(firstColumn.getByText("Card to move")).not.toBeVisible();
});

test("displays error message on API failure", async ({ page }) => {
  // Intercept API call and make it fail
  await page.route('**/api/cards', route => {
    route.abort('failed');
  });
  
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Failed card");
  await firstColumn.getByPlaceholder("Details").fill("Should fail");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  
  // Should show error message
  await expect(page.getByText(/failed to create card/i)).toBeVisible();
});
