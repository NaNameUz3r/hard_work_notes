func (c *enterpriseController) ManagerShowVehicleReports(ctx *gin.Context) {
	managerId, _ := strconv.ParseUint(ctx.Param("id"), 0, 0)
	vehicleId, _ := strconv.ParseUint(ctx.Param("vehicle_id"), 0, 0)

	if !c.authManagerVehicleUpdates(ctx, uint(vehicleId)) {
		ctx.Redirect(401, "Anauthorized")
		return
	}

	timeNB, timeNA, err := utils.UrlQTimeStampsToUTCStrings(ctx)
	if err != nil {
		log.Println(err)
	}

	selectDate := timeNB == "" && timeNA == ""
	report, _ := c.ManagerGenerateReports(ctx)
	noReports := len(report.Results) == 0

	data := gin.H{
		"selectdate": selectDate,
		"managerID":  managerId,
		"vehicleID":  vehicleId,
		"report":     report,
		"noReports":  noReports,
	}

	ctx.HTML(http.StatusOK, "reports.html", data)
}
