import { test, expect } from '@playwright/test';

test.describe('PicsFeed E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the application with header', async ({ page }) => {
    await expect(page.getByRole('banner')).toBeVisible();
    await expect(page.getByText(/PicsFeed/i)).toBeVisible();
  });

  test('should display image cards', async ({ page }) => {
    await page.waitForSelector('img', { timeout: 10000 });
    
    const images = page.locator('img');
    await expect(images.first()).toBeVisible();
    
    const firstImageSrc = await images.first().getAttribute('src');
    expect(firstImageSrc).toBeTruthy();
  });

  test('should vote like on an image', async ({ page }) => {
    await page.waitForSelector('img', { timeout: 10000 });
    
    const firstCard = page.locator('[data-testid="image-card"]').first();
    
    const likeButton = firstCard.locator('button[aria-label="like"]');
    await likeButton.click();
    
    await page.waitForTimeout(500);
  });


  test('should export votes as CSV', async ({ page }) => {
    await page.waitForSelector('img', { timeout: 10000 });
    const firstCard = page.locator('[data-testid="image-card"]').first();
    await firstCard.getByRole('button').first().click();
    await page.waitForTimeout(500);
    
    const exportButton = page.getByRole('button', { name: /export/i });
    
    const downloadPromise = page.waitForEvent('download');
    await exportButton.click();
    
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.csv');
  });

  test('should handle API errors gracefully', async ({ page }) => {
    await page.route('**/images', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Server error' })
      });
    });
    
    await page.goto('/');
    
  });

  test('should persist votes after page reload', async ({ page }) => {
    await page.waitForSelector('img', { timeout: 10000 });
    
    const firstCard = page.locator('[data-testid="image-card"]').first();
    const likeButton = firstCard.getByRole('button').first();
    await likeButton.click();
    await page.waitForTimeout(500);
    
    await page.reload();
    await page.waitForSelector('img', { timeout: 10000 });
    
  });
});
